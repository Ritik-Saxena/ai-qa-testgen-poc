import logging

def log_response(response_name, json_data):
    logging.info("#"*30)
    logging.info(f"{response_name}: START")
    logging.info("#"*30)
    logging.info(json_data)
    logging.info("#"*30)
    logging.info(f"{response_name}: END")
    logging.info("#"*30)

def log_info(info):
    logging.info("==== " + info + " ====")