import gradio as gr
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# TODO: import and run ClinSight pipeline

def analyze(image, labs, note):
    return {"esi": 3, "findings": [], "report": "Stub"}

with gr.Blocks(title="ClinSight") as demo:
    gr.Markdown("# ClinSight — Clinical Decision Support")
    with gr.Row():
        image = gr.Image(label="Chest X-ray")
        labs = gr.Textbox(label="Lab Values (JSON)")
    note = gr.Textbox(label="Triage Note")
    btn = gr.Button("Analyze")
    output = gr.JSON(label="Result")
    btn.click(analyze, inputs=[image, labs, note], outputs=output)

if __name__ == "__main__":
    demo.launch()
