# 🎬 Video Translater

> **Translate videos. Keep the voice. Keep the timing. Keep the meaning.**

**Video Translater** is an AI-powered video translation tool that automatically converts spoken content from one language into another while preserving the original video experience.

Instead of manually transcribing, translating, recording a new voice track, and synchronizing everything by hand, Video Translater turns the entire process into one automated pipeline.

Built for **Hacktoberfest Weekend 2026 — Week 1**.

---

## ✨ Why Video Translater?

Video is one of the most powerful ways to communicate, but language is still a major barrier.

A creator may have a great video in Ukrainian, Spanish, German, Japanese, or another language — but the audience may not understand it.

Traditional video localization requires several separate tools:

1. Extract the audio
2. Transcribe the speech
3. Translate the transcript
4. Generate translated speech
5. Synchronize the new audio with the video
6. Render the final video

**Video Translater combines these steps into a single workflow.**

### The goal

> **Take a video in one language and produce a naturally synchronized version in another language with as little manual work as possible.**

---

## 🚀 What It Does

Video Translater provides an automated pipeline for:

* 🎥 Video input
* 🎧 Audio extraction
* 📝 Speech transcription
* 🌍 Automatic language detection
* 🔤 Text translation
* 🗣️ AI-generated speech
* ⏱️ Audio/video synchronization
* 🎞️ Final video rendering
* 🔒 URL validation and download limits

The result is a translated video that is ready to watch or share.

---

## 🧠 How It Works

```text
                    ┌─────────────────┐
                    │   Input Video   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Audio Extraction│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Speech-to-Text  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Language Detect │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Translation   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Text-to-Speech  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Audio Sync      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Video Rendering │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Translated Video│
                    └─────────────────┘
```

---

# 🎯 Key Features

## 🌍 Automatic Translation

The application can automatically determine the source language and translate the spoken content into the requested target language.

You do not need to manually specify the source language when automatic detection is enabled.

---

## 📝 Speech Transcription

The original speech is converted into timestamped text.

Timestamps are important because translation is not just a text-processing problem — the translated speech must remain synchronized with the original video.

---

## 🗣️ AI Voice Generation

The translated text is converted back into speech.

The generated audio is then processed segment-by-segment instead of simply replacing the original audio track.

This makes it possible to preserve the timing of the original speaker.

---

## ⏱️ Smart Audio Synchronization

One of the main technical challenges in automated video translation is synchronization.

Translated speech can be longer or shorter than the original speech.

A naive implementation may:

* cut words at the end of a segment;
* create gaps between sentences;
* overlap neighboring speech;
* or produce audio that ends before the video.

Video Translater uses timestamp-aware audio processing to fit generated speech into the available timeline.

The synchronization pipeline:

```text
Original timestamps
        │
        ▼
Translated speech
        │
        ▼
Measure generated duration
        │
        ▼
Compare with available timeline
        │
        ├── Fits ──────────────► Keep audio
        │
        └── Too long
                │
                ▼
        Time-stretch audio
                │
                ▼
        Respect speed limit
                │
                ▼
        Place at original timestamp
```

The system avoids aggressively cutting generated speech when possible.

---

## 🔒 Secure Video Downloads

External URLs are an important part of a video translation service, but they can also introduce security and resource-abuse risks.

Video Translater includes download restrictions such as:

* allowed platform/domain validation;
* HTTP/HTTPS validation;
* rejection of userinfo-containing URLs;
* public-address validation;
* maximum video duration;
* maximum file size;
* network socket timeout;
* download retries;
* playlist prevention;
* temporary download directories;
* cleanup of incomplete downloads.

Default limits include:

| Limit                  |    Default |
| ---------------------- | ---------: |
| Maximum video duration |    2 hours |
| Maximum file size      |     500 MB |
| Socket timeout         | 30 seconds |
| Download retries       |          2 |
| Fragment retries       |          2 |
| Playlist downloads     |   Disabled |

These values can be adjusted for different deployment environments.

> **Production deployments should additionally isolate the downloader at the process and network level.**

---

# 🏗️ Architecture

The project is organized around separate responsibilities.

```text
Video Translater
│
├── Infrastructure
│   ├── Downloader
│   ├── Video processing
│   └── Audio processing
│
├── AI Pipeline
│   ├── Speech recognition
│   ├── Language detection
│   ├── Translation
│   └── Text-to-speech
│
└── Application
    └── Translation workflow
```

The goal is to keep external services, media processing, and application logic separated.

This makes the project easier to:

* test;
* extend;
* replace AI providers;
* add new video platforms;
* improve synchronization;
* and contribute to during Hacktoberfest.

---

# 🛠️ Technology Stack

Video Translater is built with modern Python-based media and AI tooling.

### Core

* **Python**
* **FFmpeg**
* **yt-dlp**

### AI / ML

The project uses AI models and services for:

* speech recognition;
* translation;
* text-to-speech.

The architecture is intentionally modular so individual AI components can be replaced without redesigning the complete video pipeline.

---

# 📋 Requirements

Before running the project, make sure you have:

* Python 3.10+
* FFmpeg
* Git
* Internet access for external AI/video services
* The required API/model credentials, depending on your configuration

Check your installations:

```bash
python --version
ffmpeg -version
git --version
```

---

# ⚡ Quick Start

## 1. Clone the repository

```bash
git clone https://github.com/runpy21/video-translater.git
cd video-translater
```

---

## 2. Create a virtual environment

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Install FFmpeg

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

### macOS

```bash
brew install ffmpeg
```

### Windows

Install FFmpeg and make sure the `ffmpeg` executable is available in your `PATH`.

Verify:

```bash
ffmpeg -version
```

---

# ⚙️ Configuration

Create the required environment configuration according to the project's `.env.example` file.

For example:

```bash
cp .env.example .env
```

Then configure the required API keys and application settings.

**Never commit real API keys or secrets to Git.**

A typical configuration may look like:

```env
SOURCE_LANGUAGE=auto
TARGET_LANGUAGE=en
```

The exact variables depend on the configured AI providers.

---

# ▶️ Usage

The basic workflow is:

```text
Input URL
    ↓
Download video
    ↓
Extract audio
    ↓
Transcribe
    ↓
Translate
    ↓
Generate speech
    ↓
Synchronize audio
    ↓
Render final video
```

Provide a supported video URL and select the target language.

For example:

```text
Source:
https://example.com/video

Target language:
English
```

The application processes the video and produces the translated result.

---

# 🎬 Example

Imagine you have a Ukrainian video:

```text
Original language: Ukrainian
Target language: English
```

The pipeline produces:

```text
Ukrainian Video
      │
      ▼
Ukrainian Speech
      │
      ▼
Ukrainian Transcript
      │
      ▼
English Translation
      │
      ▼
English Speech
      │
      ▼
Timestamp Synchronization
      │
      ▼
English Video
```

The important part is that the translated voice is not simply placed over the video.

It is synchronized with the original speech timeline.

---

# 🧩 Project Structure

A typical project structure looks like:

```text
video-translater/
│
├── infrastructure/
│   ├── downloader.py
│   └── video.py
│
├── ...
│
├── requirements.txt
├── .env.example
├── README.md
└── ...
```

### `infrastructure/downloader.py`

Responsible for:

* validating external URLs;
* restricting supported platforms;
* enforcing download limits;
* downloading video files;
* handling temporary files;
* cleaning up failed downloads.

### `infrastructure/video.py`

Responsible for media processing operations such as:

* extracting audio;
* reading video duration;
* synchronizing audio;
* merging audio and video;
* invoking FFmpeg.

---

# 🔐 Security Considerations

External video downloads are potentially dangerous in a public service.

The downloader therefore does not blindly accept arbitrary URLs.

It validates:

```text
URL
 │
 ├── HTTP/HTTPS?
 │
 ├── Supported domain?
 │
 ├── Valid hostname?
 │
 ├── Public destination?
 │
 └── Allowed size/duration?
        │
        ▼
      Download
```

### Resource limits

Without limits, a public service could be abused with:

* extremely large videos;
* extremely long videos;
* slow downloads;
* repeated requests;
* playlists;
* malicious or unexpected URLs.

Video Translater applies limits before and during downloading.

### Production security

For a public deployment, additional infrastructure-level protections are recommended:

* containerized downloader;
* restricted outbound network access;
* CPU/memory limits;
* process-level timeouts;
* request rate limiting;
* authentication;
* per-user quotas;
* isolated temporary storage.

---

# ⚠️ Current Limitations

Video translation is a complex problem, and the project intentionally keeps some areas open for future development.

Possible limitations include:

* generated speech may sound different from the original speaker;
* translation quality depends on the selected model/provider;
* very long videos require significant processing time;
* some platforms may change their download behavior;
* speech with heavy background noise can reduce transcription quality;
* highly different sentence lengths can make synchronization difficult;
* perfect lip synchronization is not currently guaranteed.

These limitations also represent opportunities for future contributors.

---

# 🗺️ Roadmap

## Phase 1 — Core Pipeline

* [x] Video downloading
* [x] Audio extraction
* [x] Speech transcription
* [x] Translation
* [x] Text-to-speech
* [x] Video/audio merging
* [x] Timestamp-based synchronization

## Phase 2 — Reliability

* [x] URL validation
* [x] Download size limits
* [x] Video duration limits
* [x] Download timeout handling
* [x] Temporary file cleanup
* [ ] More comprehensive automated tests
* [ ] Better error recovery

## Phase 3 — Better Localization

* [ ] Speaker detection
* [ ] Multiple speakers
* [ ] Voice preservation
* [ ] Improved prosody
* [ ] Better handling of overlapping speech
* [ ] Subtitle generation
* [ ] Multiple target languages in one job

## Phase 4 — Production

* [ ] Background job queue
* [ ] Progress tracking
* [ ] User authentication
* [ ] Rate limiting
* [ ] Containerized processing
* [ ] Resource quotas
* [ ] Cloud deployment

---

# 🧪 Testing

Run the project's test suite with:

```bash
pytest
```

For development, it is especially important to test:

### Downloader

* valid URLs;
* unsupported domains;
* invalid URLs;
* private IP destinations;
* oversized videos;
* excessively long videos;
* interrupted downloads.

### Audio synchronization

Test at least these scenarios:

```text
Short generated speech
        ↓
Normal speech
        ↓
Long generated speech
        ↓
Overlapping timestamps
        ↓
Last segment reaching video end
```

The synchronization logic should never silently destroy the end of a spoken segment just to satisfy the original timestamp.

---

# 🤝 Contributing

Contributions are welcome!

This project is especially suitable for Hacktoberfest contributors.

### Good first contributions

* Add tests
* Improve error messages
* Add support for another platform
* Improve documentation
* Improve synchronization
* Add subtitle generation
* Improve language support
* Add CLI options
* Improve logging
* Add progress reporting

### Before submitting a PR

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/my-improvement
```

3. Make your changes.
4. Run tests.

```bash
pytest
```

5. Check formatting and imports.
6. Commit your changes.

```bash
git commit -m "feat: improve video synchronization"
```

7. Push your branch.

```bash
git push origin feature/my-improvement
```

8. Open a Pull Request.

---

# 💡 Why This Project?

Video Translater is more than a simple API wrapper.

It combines several real-world engineering problems:

* multimedia processing;
* asynchronous AI workflows;
* natural language translation;
* speech synthesis;
* timestamp management;
* file management;
* external network access;
* security;
* resource management.

That makes it a practical open-source project where contributors can work on both **AI functionality and traditional software engineering**.

---

# 🏆 Hacktoberfest

Video Translater was created for **Hacktoberfest Weekend 2026 — Week 1**.

The project is designed to be contributor-friendly while solving a real problem:

> **Make video content accessible across language barriers.**

Every contribution can improve one part of the pipeline — from AI quality and synchronization to security, testing, documentation, and developer experience.

---

# 📈 What Makes It Interesting?

### For users

One workflow instead of multiple manual tools.

### For developers

A modular Python project with interesting problems across AI and infrastructure.

### For contributors

Many independent areas where meaningful improvements can be made.

### For the Hacktoberfest community

A project where contributions can have a visible, user-facing impact.

---

# 🔮 Vision

The long-term goal is to turn Video Translater into a complete open-source localization platform.

Imagine:

```text
                 ┌───────────────┐
                 │     Video     │
                 └───────┬───────┘
                         │
              ┌──────────▼──────────┐
              │   Video Translater  │
              └──────────┬──────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    English            German           Japanese
        │                │                │
        ▼                ▼                ▼
    Localized          Localized        Localized
      Video              Video            Video
```

The same original video could become accessible to audiences around the world.

---

# 📄 License

See the repository license for details.

---

# ⭐ Support the Project

If you find Video Translater useful:

* ⭐ Star the repository
* 🐛 Report bugs
* 💡 Suggest features
* 🔧 Submit pull requests
* 📖 Improve the documentation
* 🧪 Add tests
* 📢 Share the project

Every contribution helps make video content more accessible.

---

## Made with ❤️ for Hacktoberfest 2026

**Video Translater — breaking language barriers, one video at a time.**
