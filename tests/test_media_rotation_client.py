import unittest

from media_rotation_client import (
    HTTPException,
    execute_image_generation_with_fallback,
    execute_video_generation_with_fallback,
)


class MediaRotationClientTests(unittest.TestCase):
    def test_image_fallback_rotates_when_first_provider_rate_limits(self):
        calls = []

        def provider_one(prompt):
            calls.append("image-1")
            raise HTTPException(status_code=429, detail={"error": "rate_limited"})

        def provider_two(prompt):
            calls.append("image-2")
            return {"ok": True, "provider": "image-2"}

        result = execute_image_generation_with_fallback(
            "test prompt",
            provider_callables=[provider_one, provider_two],
            api_keys=["key-1", "key-2"],
        )

        self.assertEqual(result["provider"], "image-2")
        self.assertEqual(calls, ["image-1", "image-2"])

    def test_video_fallback_rotates_when_provider_is_quota_exhausted(self):
        calls = []

        def provider_one(prompt):
            calls.append("video-1")
            raise HTTPException(status_code=402, detail={"error": "payment_required"})

        def provider_two(prompt):
            calls.append("video-2")
            return {"ok": True, "provider": "video-2"}

        result = execute_video_generation_with_fallback(
            "test prompt",
            provider_callables=[provider_one, provider_two],
            api_keys=["video-key-1", "video-key-2"],
        )

        self.assertEqual(result["provider"], "video-2")
        self.assertEqual(calls, ["video-1", "video-2"])

    def test_all_image_providers_exhausted_raise_503(self):
        def provider_one(prompt):
            raise HTTPException(status_code=429, detail={"error": "rate_limited"})

        def provider_two(prompt):
            raise HTTPException(status_code=402, detail={"error": "payment_required"})

        with self.assertRaises(HTTPException) as cm:
            execute_image_generation_with_fallback(
                "test prompt",
                provider_callables=[provider_one, provider_two],
                api_keys=["key-1", "key-2"],
            )

        self.assertEqual(cm.exception.status_code, 503)

    def test_missing_keys_are_skipped_for_video_rotation(self):
        def provider_one(prompt):
            raise HTTPException(status_code=429, detail={"error": "rate_limited"})

        def provider_two(prompt):
            return {"ok": True, "provider": "video-2"}

        result = execute_video_generation_with_fallback(
            "test prompt",
            provider_callables=[provider_one, provider_two],
            api_keys=[None, "video-key-2"],
        )

        self.assertEqual(result["provider"], "video-2")


if __name__ == "__main__":
    unittest.main()
