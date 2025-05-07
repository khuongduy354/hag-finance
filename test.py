import solution


def test_time_interval():
    res = solution.is_in_time_interval(
    {'Thời gian': '14:45:09'},
    {'Thời gian': '14:45:10'},
    1 
    )  
    assert res == True, f"Expected True, but got {res}" 

if __name__ == "__main__":
    print("Running test...")
    test_time_interval()