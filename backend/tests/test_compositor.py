import os
import pytest
from PIL import Image
from app.services.image_gen_service import GreetingCompositor

def test_greeting_compositor_generates_valid_image():
    for fest in ["diwali", "holi", "eid_ul_fitr", "christmas", "new_year", "independence_day_in", "durga_puja"]:
        out_path, img_url, metrics = GreetingCompositor.generate_greeting_image(
            festival_slug=fest,
            greeting_text=f"Celebration of {fest}",
            width=1080,
            height=1080,
            custom_palette=["#1E3A8A", "#D97706"]
        )
        assert os.path.exists(out_path)
        assert metrics["width"] == 1080
        assert metrics["height"] == 1080
        assert metrics["spelling_integrity"] == "DETERMINISTIC_VERIFIED"

        # Verify image is valid PIL image
        with Image.open(out_path) as img:
            assert img.size == (1080, 1080)
            assert img.format in ["PNG", "JPEG"]

        # Clean up test output
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except Exception:
                pass
