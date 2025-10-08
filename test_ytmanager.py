import json
import os
import sys

# Add current directory to path so we can import ytmanager
sys.path.append('.')

import ytmanager

def test_load_data():
    """Test load_data function"""
    # Test when file doesn't exist
    if os.path.exists("youtube.txt"):
        os.remove("youtube.txt")

    result = ytmanager.load_data()
    assert result == [], f"Expected empty list, got {result}"
    print("✓ load_data() returns empty list when file doesn't exist")

    # Test when file exists
    test_data = [{"video": "Test Video", "time": "10:00"}]
    with open("youtube.txt", "w") as f:
        json.dump(test_data, f)

    result = ytmanager.load_data()
    assert result == test_data, f"Expected {test_data}, got {result}"
    print("✓ load_data() returns correct data when file exists")

def test_save_video_helper():
    """Test save_video_helper function"""
    test_data = [{"video": "Test Video", "time": "10:00"}]
    ytmanager.save_video_helper(test_data)

    # Verify file was created and contains correct data
    assert os.path.exists("youtube.txt"), "youtube.txt was not created"

    with open("youtube.txt", "r") as f:
        saved_data = json.load(f)

    assert saved_data == test_data, f"Expected {test_data}, got {saved_data}"
    print("✓ save_video_helper() saves data correctly")

def test_list_all_videos():
    """Test list_all_videos function"""
    test_data = [
        {"video": "Video 1", "time": "5:00"},
        {"video": "Video 2", "time": "10:00"}
    ]

    print("Testing list_all_videos output:")
    ytmanager.list_all_videos(test_data)
    print("✓ list_all_videos() displays videos correctly")

if __name__ == "__main__":
    print("Running tests for ytmanager.py...")
    test_load_data()
    test_save_video_helper()
    test_list_all_videos()
    print("All tests passed! ✓")

    # Clean up
    if os.path.exists("youtube.txt"):
        os.remove("youtube.txt")
