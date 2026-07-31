"""
conftest.py - Test collection ordering for Day 10 to match Sekil 20 report standards.
"""

def pytest_collection_modifyitems(items):
    file_order = [
        "test_order_points.py",
        "test_homography.py",
        "test_corner_detector.py",
        "test_rectification.py",
        "test_cli.py",
    ]
    def sort_key(item):
        fname = str(item.fspath)
        for idx, target in enumerate(file_order):
            if target in fname:
                return idx
        return len(file_order)

    items.sort(key=sort_key)
