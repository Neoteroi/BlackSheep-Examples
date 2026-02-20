"""
Example: Upload files using multipart/form-data with the BlackSheep HTTP Client.

This example demonstrates efficient file uploading using the MultiPartFormData class
with the ClientSession. Files are read from disk using file handles, which allows
for memory-efficient streaming without loading entire files into memory at once.
"""

import asyncio
from io import BytesIO
from pathlib import Path
from essentials.diagnostics import StopWatch

from blacksheep.client import ClientSession
from blacksheep.contents import FormPart, MultiPartFormData


async def upload_files_example():
    """
    Example: Upload multiple files using multipart/form-data.

    This demonstrates uploading files efficiently using the FormPart
    convenience methods that handle encoding and file operations.
    """
    async with ClientSession() as session:
        # Create form parts using convenience methods
        # Create multipart content
        content = MultiPartFormData([
            # Text field
            FormPart.field(
                "description",
                "Important documents for review",
            ),
            # First file upload
            FormPart.from_file(
                "example-video",
                "example-video.mp4",
            ),
            # Second file upload
            FormPart.from_file(
                "avatar",
                "my-avatar.jpeg",
            ),
        ])

        # Send the request
        with StopWatch() as sw:
            response = await session.post(
                "http://127.0.0.1:44555/upload-text",
                content=content,
            )

        print(f"Upload status: {response.status}")
        print(f"Response: {await response.text()}")
        print(f"Elapsed: {sw.elapsed_s}s")


async def upload_generated_data_example():
    """
    Example: Upload programmatically generated data using BytesIO.

    This is useful when you're creating files in memory or want to upload
    data that doesn't come from a file on disk. For in-memory data, we still
    use the traditional FormPart constructor with BytesIO objects.
    """
    async with ClientSession() as session:
        # Create some data in memory
        csv_data = BytesIO(
            b"name,email,age\n"
            b"John Doe,john@example.com,30\n"
            b"Jane Smith,jane@example.com,25\n"
        )

        json_data = BytesIO(b'{"status": "processed", "count": 42}')

        response = await session.post(
            "http://127.0.0.1:44555/process",
            content=MultiPartFormData([
                # For BytesIO objects, use the traditional constructor
                FormPart(
                    name=b"csv_file",
                    data=csv_data,
                    file_name=b"data.csv",
                    content_type=b"text/csv",
                ),
                FormPart(
                    name=b"metadata",
                    data=json_data,
                    file_name=b"metadata.json",
                    content_type=b"application/json",
                ),
            ]),
        )

        print(f"Status: {response.status}")


async def upload_with_mixed_sources():
    """
    Example: Mix different data sources in one multipart upload.

    This shows the flexibility of FormPart - you can combine:
    - Files from disk (using from_file())
    - In-memory data (using traditional constructor with BytesIO)
    - Simple text fields (using field())
    """
    async with ClientSession() as session:
        # Check if file exists before opening
        config_path = Path("config.json")

        # Create thumbnail data in memory
        thumbnail = BytesIO(b"\x89PNG\r\n\x1a\n...")  # Mock PNG header

        parts = [
            # Simple text field - use field()
            FormPart.field("user_id", "12345"),
            # Form field with value
            FormPart.field("tags", "important,urgent"),
        ]

        # Add config file if it exists, otherwise use BytesIO
        if config_path.exists():
            # File from disk - use from_file()
            parts.append(
                FormPart.from_file(
                    "config",
                    "config.json",
                    content_type="application/json",
                )
            )
        else:
            print(f"File {config_path} not found, using sample data...")
            # BytesIO fallback - use traditional constructor
            parts.append(
                FormPart(
                    name=b"config",
                    data=BytesIO(b'{"env": "production"}'),
                    file_name=b"config.json",
                    content_type=b"application/json",
                )
            )

        # In-memory generated file - use traditional constructor
        parts.append(
            FormPart(
                name=b"thumbnail",
                data=thumbnail,
                file_name=b"thumb.png",
                content_type=b"image/png",
            )
        )

        content = MultiPartFormData(parts)

        response = await session.post(
            "http://127.0.0.1:44555/submit",
            content=content,
            headers={"X-API-Key": "your-api-key"},
        )

        print(f"Status: {response.status}")


async def upload_large_file_efficiently():
    """
    Example: Upload a large file efficiently.

    The from_file() method automatically opens the file and handles it,
    streaming the content in chunks rather than loading it entirely into memory.
    This is memory-efficient for large files.
    """
    async with ClientSession() as session:
        # For large files, use from_file() which handles the file efficiently
        parts = [
            # Text field
            FormPart.field("title", "My Video Upload"),
            # Large file - from_file() handles streaming automatically
            FormPart.from_file(
                "video",
                "large_video.mp4",
                content_type="video/mp4",
            ),
        ]

        content = MultiPartFormData(parts)

        # The file will be streamed in chunks during upload
        response = await session.post(
            "http://127.0.0.1:44555/videos/upload",
            content=content,
        )

        print(f"Upload complete: {response.status}")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("BlackSheep HTTP Client - Multipart Upload Examples")
    print("=" * 60)

    # Note: These examples require actual files and endpoints
    # Uncomment the one you want to test

    await upload_files_example()
    # await upload_generated_data_example()
    # await upload_with_mixed_sources()
    # await upload_large_file_efficiently()

    print("\nExamples are commented out. Uncomment the one you want to test.")
    print("Make sure to have the required files and update the endpoint URLs.")


if __name__ == "__main__":
    asyncio.run(main())
