import unittest
import base64
from pathlib import Path

from treasury.services.gateways.ttb_api.main.adapter.out.llm.openai_adapter import OpenAiAdapter


class TestOpenAiAdapter(unittest.TestCase):

    def setUp(self) -> None:
        self.adapter = OpenAiAdapter()

        # Load the test image
        test_assets_dir = Path(__file__).parent.parent.parent.parent / "assets"
        image_path = test_assets_dir / "tanqueray_london_dry_gin.png"

        if not image_path.exists():
            raise FileNotFoundError(f"Test image not found: {image_path}")

        # Read and encode image
        with open(image_path, 'rb') as f:
            self.image_bytes = f.read()
            self.base64_image = base64.b64encode(self.image_bytes).decode('utf-8')
            self.base64_with_prefix = f"data:image/png;base64,{self.base64_image}"


if __name__ == '__main__':
    unittest.main()
