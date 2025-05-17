import main


def test_time_interval():
    res = main.is_in_time_interval(
    {'Thời gian': '14:45:09'},
    {'Thời gian': '14:45:10'},
    1 
    )  
    assert res == True, f"Expected True, but got {res}" 


def test_color_gen():    
    res = main.generate_next_color("#FF5733") 
    print(f"Next color: {res}")

if __name__ == "__main__": 
    test_color_gen()
    print("Running test...")
    test_time_interval()