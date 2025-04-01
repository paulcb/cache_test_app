import random
import sys


def makesqlfile(foldername, trace_file_path, test_name):
    filename = f'{foldername}/{trace_file_path}'
    outfilename = f'{foldername}/{trace_file_path}.sql'

    num_lines = sum(1 for _ in open(filename))
    chunk = 100000
    # print('num_lines', num_lines)
    keys = set()

    f1 = open(filename, 'r')
    f2 = open(outfilename, 'w')

    start = f"""
    CREATE TABLE IF NOT EXISTS {test_name} (
        id SERIAL PRIMARY KEY,
        orig_key VARCHAR NOT NULL UNIQUE,
        orig_value VARCHAR NOT NULL
    );
    DELETE FROM {test_name};
    """

    f2.write(start)
    count = 1
    rows = []
    for line in f1:

        lineSplit = line.split()
        key = lineSplit[0]
        num_blocks = 1
        if len(lineSplit) > 1:
            num_blocks = int(lineSplit[1])
        
        if key in keys:
            continue
        keys.add(key)
        row = f"('{key}', '{random.randbytes(16 * num_blocks).hex()}')"
        rows.append(row)

        if count >= chunk:
            endpart = f"""

    INSERT INTO {test_name} (orig_key, orig_value)
    VALUES

            """
            f2.write(endpart)
            rowsContent = ""
            for r in rows:
                rowsContent += r + ',\n' 
            rowsContent = rowsContent[:-2]
            rowsContent += ';\n'
            f2.write(rowsContent)
            count = 0
            rows.clear()
            continue

        count += 1
    
    if(len(rows) > 0):
        endpart = f"""

    INSERT INTO {test_name} (orig_key, orig_value)
    VALUES

            """
        f2.write(endpart)
            
        rowsContent = ""
        for r in rows:
            rowsContent += r + ',\n' 
        rowsContent = rowsContent[:-2]
        rowsContent += ';\n'
        f2.write(rowsContent)
    print('filename', filename)        
    print('num reqs', num_lines)
    print('num keys', len(keys))
    f1.close()
    f2.close()

folder_name = sys.argv[1]
