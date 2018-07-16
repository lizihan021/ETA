import json

def process_json(input_json_file, output_json_file, path):
    file_in = open(input_json_file, "r")
    file_out = open(output_json_file, "w")
    # load data to json_data
    json_data = json.load(file_in)

    # edit json data
    coordinates = []
    for edge in path:
        coordinates.append([edge.start_x, edge.start_y])
    # print coordinates
    json_data["source"]["data"]["geometry"]["coordinates"] = coordinates
    
    # json_data["job"] = "hahah"
    # print json_data
    
    # write back data
    file_out.write(json.dumps(json_data, sort_keys=True, indent=4, separators=(',', ': ')))
    file_in.close()
    file_out.close()

def path2json(input_json_file, output_json_file, path):
    process_json(input_json_file, output_json_file, path)

