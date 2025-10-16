import gradio as gr
from gradio_client import Client, handle_file
from pydub import AudioSegment
import tempfile, requests

# Kết nối đến model TTS gốc
tts_client = Client("hynt/F5-TTS-Vietnamese-100h")

# File giọng mẫu (có thể thay bằng URL khác nếu muốn clone giọng)
ref_audio_url = "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav"
ref_audio = handle_file(ref_audio_url)

def synthesize(text, pause_duration):
    if not text.strip():
        return None, "❌ Vui lòng nhập nội dung."
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    segments = []
    for i, line in enumerate(lines, start=1):
        print(f"Đang đọc dòng {i}: {line}")
        try:
            result = tts_client.predict(
                ref_audio_orig=ref_audio,
                gen_text=line,
                speed=1,
                api_name="/infer_tts"
            )
            r = requests.get(result)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file.write(r.content)
            temp_file.close()

            segments.append(AudioSegment.from_wav(temp_file.name))
            segments.append(AudioSegment.silent(duration=pause_duration * 1000))
        except Exception as e:
            print("Lỗi khi đọc:", line, e)

    if not segments:
        return None, "❗ Không tạo được âm thanh."
    final_audio = sum(segments)
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    final_audio.export(output_path, format="wav")

    return output_path, f"✅ Hoàn tất! Đã đọc {len(lines)} dòng."

demo = gr.Interface(
    fn=synthesize,
    inputs=[
        gr.Textbox(
            label="Nhập văn bản (mỗi dòng = 1 câu)",
            lines=10,
            placeholder="Ví dụ:\nXin chào.\nMình là ChatGPT."
        ),
        gr.Slider(0.5, 5, value=1.5, step=0.5, label="Thời gian nghỉ giữa dòng (giây)")
    ],
    outputs=[
        gr.Audio(label="Kết quả đọc"),
        gr.Textbox(label="Trạng thái")
    ],
    title="SPT - Vietnamese Multi-line TTS",
    description="Đọc từng dòng văn bản tiếng Việt bằng model hynt/F5-TTS-Vietnamese-100h, có ngắt nghỉ giữa các câu."
)

if __name__ == "__main__":
    demo.launch()
