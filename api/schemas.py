
def new_pet(data):
    return {
        "petID": data.get("petID"),
        "name": data.get("name"),
        "species": data.get("species"),
        "breed": data.get("breed"),
        "sex": data.get("sex"),
        "dob": data.get("dob"),
        "neutered": data.get("neutered", False),
        "insurance_id": data.get("insurance_id"),
        "weight": data.get("weight"),
        "vaccine_list": data.get("vaccine_list", []),
        "reminders": data.get("reminders", []),
        "ui_preference": data.get("ui_preference"),
    }

def new_user(data):
    return {
        "userID": data.get("userID"),
        "name": data.get("name"),
        "phone_no": data.get("phone_no"),
        "address": data.get("address"),
        "dob": data.get("dob"),
        "pet_id_list": data.get("pet_id_list", []),
    }
