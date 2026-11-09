import json
import shutil
import subprocess
from array import array
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from starlette.testclient import TestClient

import shorts_api
from core import shorts
from server import app

VIDEO = "https://www.youtube.com/watch?v=abcdefghijk"


@pytest.mark.parametrize(
    "url",
    [
        "https://youtu.be/abcdefghijk?t=45",
        VIDEO + "&list=playlist",
        "https://m.youtube.com/shorts/abcdefghijk",
    ],
)
def test_accepts_one_youtube_video(url):
    assert shorts.youtube_url(url) == VIDEO


@pytest.mark.parametrize(
    "url",
    [
        "https://youtube.com.example/watch?v=abcdefghijk",
        "https://youtube.com@127.0.0.1/watch?v=abcdefghijk",
        "https://www.youtube.com/playlist?list=foo",
        "file:///some/video.mp4",
    ],
)
def test_rejects_other_sources(url):
    with pytest.raises(ValueError):
        shorts.youtube_url(url)


def test_local_api_requires_configuration_and_rejects_foreign_origins(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with TestClient(app, base_url="http://localhost") as client:
        assert client.post("/api/shorts", json={"url": VIDEO}).status_code == 503
        assert client.post("/api/shorts", json={"url": "/tmp/test.mp4"}).status_code == 400
        assert (
            client.post(
                "/api/shorts", headers={"Origin": "https://example.org"}, json={"url": VIDEO}
            ).status_code
            == 403
        )
        assert (
            client.post(
                "/api/shorts", headers={"Host": "example.org"}, json={"url": VIDEO}
            ).status_code
            == 403
        )
        assert client.post("/api/shorts", content=VIDEO).status_code == 415


def test_groq_rate_limit_does_not_disclose_key(monkeypatch):
    monkeypatch.setattr(shorts.requests, "post", lambda *a, **k: SimpleNamespace(status_code=429))
    with pytest.raises(shorts.ShortsError, match="rate limit") as error:
        shorts._groq_post("private-fixture-key", "/chat/completions")
    assert "private-fixture-key" not in str(error.value)


def _chat_response(clips):
    return {"choices": [{"message": {"content": json.dumps({"clips": clips})}}]}


def _metadata(candidate):
    return {
        "id": candidate,
        "title": f"Video highlight {candidate}",
        "description": "A distinct moment from the source video.",
        "hashtags": ["#Video", "Relent", "Highlight"],
        "hook": "A quick highlight",
    }


def test_refuses_duplicate_model_choices(monkeypatch):
    monkeypatch.setattr(
        shorts, "_groq_post", lambda *a, **k: _chat_response([_metadata(0), _metadata(0)])
    )
    word = shorts.Word(1, 2, "test")
    with pytest.raises(shorts.ShortsError, match="unique clips"):
        shorts._rank("test", [[word], [word]])


def test_short_source_requests_only_its_usable_candidates(monkeypatch):
    words = [shorts.Word(i, i + 0.9, "speech") for i in range(21)]
    candidates = shorts._candidates(words, 21)
    assert len(candidates) == 1

    def chat(key, endpoint, **kwargs):
        assert len(json.loads(kwargs["json"]["messages"][1]["content"])) == 1
        return _chat_response([_metadata(0)])

    monkeypatch.setattr(shorts, "_groq_post", chat)
    assert len(shorts._rank("test", candidates)) == 1


@pytest.mark.integration
def test_api_produces_ten_captioned_shorts_with_original_audio(tmp_path, monkeypatch):
    if not all(shutil.which(binary) for binary in ("ffmpeg", "ffprobe")):
        pytest.skip("FFmpeg and FFprobe are required for the media integration test")
    source = tmp_path / "source.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:s=160x90:r=8",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=16000",
            "-t",
            "215",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            str(source),
        ],
        check=True,
        timeout=30,
    )
    output = tmp_path / "outputs"
    monkeypatch.setattr(shorts_api, "SHORTS_DIR", output)
    monkeypatch.setenv("GROQ_API_KEY", "fixture-key")

    def download(url, work):
        assert url == VIDEO
        shutil.copyfile(source, work / "input.video")

    offsets = iter(range(0, 215, shorts.AUDIO_CHUNK))

    def post(url, *, headers, allow_redirects, timeout, **kwargs):
        assert headers == {"Authorization": "Bearer fixture-key"}
        assert allow_redirects is False and timeout
        if url.endswith("/audio/transcriptions"):
            assert kwargs["data"]["timestamp_granularities[]"] == "word"
            filename, audio, mime = kwargs["files"]["file"]
            assert (filename, mime) == ("audio.mp3", "audio/mpeg")
            assert audio.read(3) == b"ID3"
            assert Path(audio.name).stat().st_size < 250_000
            offset = next(offsets)
            result = {
                "words": [
                    {
                        "word": "sentence." if (offset + i) % 16 == 15 else "word",
                        "start": i,
                        "end": i + 0.9,
                    }
                    for i in range(min(shorts.AUDIO_CHUNK, 215 - offset))
                ]
            }
        else:
            assert url.endswith("/chat/completions")
            choices = json.loads(kwargs["json"]["messages"][1]["content"])
            assert len(choices) > 10
            result = _chat_response([_metadata(item["id"]) for item in choices[-1:-11:-1]])
        return SimpleNamespace(status_code=200, json=lambda: result)

    monkeypatch.setattr(shorts, "_download", download)
    monkeypatch.setattr(shorts.requests, "post", post)
    with TestClient(app, base_url="http://127.0.0.1") as client:
        response = client.post("/api/shorts", json={"url": VIDEO})
        assert response.status_code == 201, response.text
        batch = response.json()
        assert batch["requested_count"] == len(batch["clips"]) == 10
        assert "fixture-key" not in response.text
        metadata = client.get(batch["metadata_url"])
        assert metadata.json()["clips"] == batch["clips"]
        assert len(list(output.iterdir())) == 1
        batch_path = next(output.iterdir())
        for index, clip in enumerate(batch["clips"], start=1):
            assert clip["title"] and clip["description"] and clip["hook"]
            assert clip["hashtags"] == ["#Video", "#Relent", "#Highlight"]
            assert clip["source_end"] - clip["source_start"] >= 15
            media = client.get(clip["video_url"], headers={"Range": "bytes=0-31"})
            assert media.status_code == 206 and media.content[4:8] == b"ftyp"
            artifact = batch_path / f"short-{index:02}.mp4"
            result = subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_streams",
                    "-show_format",
                    "-of",
                    "json",
                    str(artifact),
                ],
                text=True,
            )
            video, audio = json.loads(result)["streams"]
            assert (video["codec_name"], video["width"], video["height"]) == ("h264", 720, 1280)
            assert audio["codec_name"] == "aac"
            assert float(json.loads(result)["format"]["duration"]) == pytest.approx(
                clip["source_end"] - clip["source_start"], abs=0.12
            )
        first = batch["clips"][0]["video_url"]
        download_headers = client.head(first + "?download=1").headers
        assert 'attachment; filename="short-01.mp4"' in download_headers["content-disposition"]
        assert client.get(first.rsplit("/", 1)[0] + "/11").status_code == 404

    # The source is solid blue. Bright RGB pixels in the caption area after the
    # hook has expired prove subtitle glyphs are present in the encoded video.
    frame = subprocess.check_output(
        [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            "6.2",
            "-i",
            str(batch_path / "short-01.mp4"),
            "-vf",
            "crop=720:150:0:910",
            "-frames:v",
            "1",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ]
    )
    assert any(min(frame[i : i + 3]) > 160 for i in range(0, len(frame), 3))

    pcm = subprocess.check_output(
        [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            "5",
            "-i",
            str(batch_path / "short-01.mp4"),
            "-t",
            "1",
            "-vn",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-f",
            "s16le",
            "-",
        ]
    )
    samples = array("h", pcm)
    assert max(samples) > 1000
    rising_edges = sum(a <= 0 < b for a, b in zip(samples, samples[1:], strict=False))
    assert rising_edges == pytest.approx(440, abs=5)


def test_render_failure_leaves_no_published_batch(tmp_path, monkeypatch):
    monkeypatch.setattr(shorts, "_download", lambda *a: None)
    probe = {
        "format": {"duration": 20},
        "streams": [{"codec_type": "video"}, {"codec_type": "audio"}],
    }
    monkeypatch.setattr(shorts, "_run", lambda *a: json.dumps(probe))
    words = [shorts.Word(i, i + 0.9, "speech") for i in range(20)]
    monkeypatch.setattr(shorts, "_transcribe", lambda *a: words)
    monkeypatch.setattr(shorts, "_rank", lambda *a: [_metadata(0)])
    monkeypatch.setattr(shorts.shutil, "which", lambda name: name)

    def fail(*args):
        raise shorts.ShortsError("Fixture render error")

    monkeypatch.setattr(shorts, "_render", fail)
    with pytest.raises(shorts.ShortsError, match="Fixture render error"):
        shorts.generate_shorts(VIDEO, "test", Path(tmp_path), "failed-batch")
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("configured", [False, True])
def test_youtube_download_respects_configured_tls(tmp_path, monkeypatch, configured):
    import yt_dlp

    monkeypatch.delenv("SSL_CERT_FILE", raising=False)
    monkeypatch.delenv("SSL_CERT_DIR", raising=False)
    if configured:
        monkeypatch.setenv("SSL_CERT_FILE", "/fixture/ca-bundle.pem")

    class Downloader:
        def __init__(self, options):
            assert ("no-certifi" in options.get("compat_opts", ())) is configured
            assert not options.get("nocheckcertificate")

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def download(self, urls):
            assert urls == [VIDEO]
            (tmp_path / "source.mp4").write_bytes(b"fixture")

    monkeypatch.setattr(yt_dlp, "YoutubeDL", Downloader)
    shorts._download(VIDEO, tmp_path)
    assert (tmp_path / "input.video").read_bytes() == b"fixture"


@pytest.mark.parametrize("merge_failed", [False, True])
def test_reports_html_media_response(tmp_path, monkeypatch, merge_failed):
    import yt_dlp
    from yt_dlp.utils import DownloadError

    class Downloader:
        def __init__(self, options):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def download(self, urls):
            (tmp_path / "source.f18.mp4").write_bytes(
                b"\n<!DOCTYPE HTML><title>Site Unavailable</title>"
            )
            if merge_failed:
                raise DownloadError("Postprocessing failed")

    monkeypatch.setattr(yt_dlp, "YoutubeDL", Downloader)
    with pytest.raises(shorts.ShortsError, match="returned a web page"):
        shorts._download(VIDEO, tmp_path)
    assert not (tmp_path / "input.video").exists()


def test_groq_audio_upload_retries_once_with_the_complete_body(monkeypatch):
    payload = b"test audio"
    audio = BytesIO(payload)
    attempts = []

    def post(url, **kwargs):
        attempts.append(kwargs["files"]["file"][1].read())
        if len(attempts) == 1:
            raise shorts.requests.ConnectionError("fixture disconnect")
        return SimpleNamespace(status_code=200, json=lambda: {"words": []})

    monkeypatch.setattr(shorts.requests, "post", post)
    result = shorts._groq_post(
        "test", "/audio/transcriptions", files={"file": ("audio.mp3", audio, "audio/mpeg")}
    )
    assert attempts == [payload, payload]
    assert result == {"words": []}
