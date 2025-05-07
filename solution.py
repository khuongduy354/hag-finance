import itertools 
import datetime
import input_handler


def is_giao_dich(row)->bool:   
    must_not_change_field = ["Khối lượng", "Giá", "Loại"]   

    for f in must_not_change_field:   
        if row[f] != "":
            return False  
    return True 

def is_lenh(row)->bool: 
    return not is_giao_dich(row)

def is_in_time_interval(t1: dict, t2: dict, interval: int = 1) -> bool:  
    t1 = t1["Thời gian"]
    t2 = t2["Thời gian"]
    """
    Kiểm tra xem t1 và t2 có cách nhau interval giấy không 
    """
    time_format = "%H:%M:%S"
    t1_obj = datetime.datetime.strptime(t1, time_format)
    t2_obj = datetime.datetime.strptime(t2, time_format)
    
    # Tính khoảng cách giữa hai thời gian
    delta = abs((t2_obj - t1_obj).total_seconds())
    
    return delta <= interval

def get_list(l: list, idx:int):  
    if idx < 0:   
        return None  

    if idx >= len(l): 
        return None 

    return l[idx]

def lambda_in_time(t1:dict, interval:int = 1):  
    return lambda x: is_in_time_interval(t1, x, interval) or is_in_time_interval(x, t1, interval)

def get_row_at_idx(l: list, idx: int, c: list[callable]):  
    item = get_list(l,idx)  
    if item is None: 
        return None 
    else:
        for func in c:
            if not func(item): 
                return None
        return item


def fix_sync(all_rows: list) -> list:     
    new_rows = all_rows.copy()

    # Gom cụm
    i = 0 
    chunk = []
    chunks:list[list] = [] 
    while i < len(all_rows):
        if is_lenh(all_rows[i]):           
            curr_lenh = all_rows[i] 

            # Lấy giao dịch tiếp theo trong interval 
            next_gd = get_row_at_idx(all_rows, i+1, [is_giao_dich, lambda_in_time(curr_lenh)]) 
            if next_gd is not None:    
                # Thêm lệnh hiện tại
                chunk.append({"row": curr_lenh, "idx": i}) 
                # Thêm giao dịch tiếp theo
                i+=1
                chunk.append({"row": next_gd, "idx": i}) 

                # Lấy lệnh tiếp tiếp theo (sau giao dịch)  
                next_next_lenh = get_row_at_idx(all_rows, i+2, [is_lenh, lambda_in_time(next_gd)]) 
                if next_next_lenh is not None:  
                    # Thêm lệnh tiếp tiếp theo
                    i+=1
                    chunk.append({"row": next_next_lenh, "idx": i}) 

            # Thêm vào ds cụm
            if len(chunk) > 0: 
                chunks.append(chunk) 
                chunk = []
        i+=1

    logs = [] 
    print("Tổng số cụm: ", len(chunks))  

    # TODO: fix chunk here, some list, some dict
    for i,_chunk in enumerate(chunks):     
        if len(_chunk) <= 1:  
            # Nếu chỉ có 1 dòng thì không cần xử lý
            continue  

        _chunk = sorted(_chunk, key=lambda x: x["row"]["Thời gian"]) 
        chunk = [x["row"] for x in _chunk]  
        start_row = _chunk[0]["idx"]

        # Nhớ thứ tự 
        giao_dich_order = list(filter(is_giao_dich,chunk))
        lenh_order = list(filter(lambda x: not is_giao_dich(x), chunk))
        
        # Hoán vị    
        perms = [list (p) for p in itertools.permutations(chunk)]

        # Lọc các hoán vị không đúng thứ tự 
        valid_perms = []
        for p in perms:      
            giao_dich_part = list(filter(is_giao_dich, p))
            lenh_part = list(filter(lambda x: not is_giao_dich(x), p))

            if giao_dich_part == giao_dich_order and lenh_part == lenh_order:  
                valid_perms.append(p) 


        # Tính tổng    
        min_sum = float("inf") 
        best_perm_idx = -1   
        for i,p in enumerate(valid_perms):     
            sum = 0 

            # Lấy độ lệch từng hoán vị
            for j,row in enumerate(p):   
                if j == len(p) - 1:
                    # Nếu là dòng cuối thì không cần tính
                    continue

                delta = 0 

                # Dòng lệnh: Tăng/giảm = Chờ_mới - Chờ_cũ + KL_lệnh. 
                next_row = p[j+1]    
                if not is_giao_dich(row):    
                    delta = next_row["Chờ mua 1"] - row["Chờ mua 1"] + input_handler.to_float(row["Khối lượng"])  
                else: 
                    # Dòng giao dịch: Tăng/giảm = Chờ_mới - Chờ_cũ (không cộng KL_lệnh).
                    delta = next_row["Chờ mua 1"] - row["Chờ mua 1"] 
                 
                sum += abs(delta) 

            # Chọn hoán vị tổng nhỏ nhất
            if sum < min_sum:  
                min_sum = sum
                best_perm_idx = i
        
        # Gán lại thứ tự cho cụm
        if best_perm_idx == -1: 
            print("Lỗi không tìm thấy hoán vị nào hợp lệ") 
            raise Exception("Lỗi không tìm thấy hoán vị nào hợp lệ") 

        best_perm = valid_perms[best_perm_idx]    
        if len(best_perm) != len(chunk):  
            print("Lỗi hoán vị không có cùng số rows với cụm ban đầu: ", len(best_perm), len(chunk)) 
            raise Exception("Lỗi: ", len(best_perm), len(chunk))

        new_rows[start_row:start_row + len(chunk)] = best_perm


        changed = chunk == best_perm
        logs.append({  
            "Size of chunk: ": len(chunk),
            "Row ảnh hưởng": str(start_row) + "-" + str(start_row + len(chunk) - 1),
            "Có thay đổi: ": changed,  
            "Message: ": "Đã hoán vị cụm này" if changed else "Không có thay đổi",
        })   



    
    return new_rows, logs