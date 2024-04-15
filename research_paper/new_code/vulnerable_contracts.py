import json
import logging
import func_timeout
from teether.exploit import combined_exploit
from teether.project import Project
from teether.util.utils import denoms
import os

#Refactored https://github.com/duytai/teether/blob/master/bin/gen_exploit.py

def list_files(directory):
    file_paths = []
    # Walk through all files and subdirectories in the directory
    for root, _ , files in os.walk(directory):
        # Iterate through files
        for filename in files:
            # Join the root path with the filename to get the complete file path
            file_path = os.path.join(root, filename)
            # Append the file path to the list
            file_paths.append(file_path)
    return file_paths

# setting  default values
target_addr = 0x1234123412341234123412341234123412341234
shellcode_addr = 0x1000000000000000000000000000000000000000
amount = 1000
amount_check = '+'
initial_storage = {}
initial_balance = 10 * denoms.ether

# Critical Instructions
flags =  {'CALL', 'CALLCODE', 'DELEGATECALL', 'SELFDESTRUCT'}
def hex_encode(d):
    return {k: v.hex() if isinstance(v, bytes) else v for k, v in d.items()}

def run_combined_attack(code_path):
    logging.info(code_path)
    with open(code_path) as infile:
        inbuffer = infile.read().rstrip()
    code = bytes.fromhex(inbuffer)
    p = Project(code)
    savefilebase = code_path.split('/')[-1]
    result = None
    try:
        result = func_timeout.func_timeout(1200.0, combined_exploit, args=[p, target_addr, shellcode_addr, amount, amount_check,
                                                                            initial_storage, initial_balance, flags])
    except func_timeout.FunctionTimedOut:
        return False
    except Exception as e:
        print("Something went wrong. Exception is  {e}")

    if result:
        call, r, model = result
        logging.info(model)
        with open(f'{savefilebase}.exploit.json', 'w') as f:
            json.dump({'paths': [{'index': i, 'path': [ins for ins in res.state.trace if
                                                       ins in p.cfg.bb_addrs or ins == res.state.trace[-1]]} for
                                 i, res in enumerate(r.results)],
                       'calls': [{'index': i, 'call': hex_encode(c)} for i, c in enumerate(call)]}, f)
        for i, res in enumerate(r.results):
            logging.info(f'{i}: {"->".join([f"{i:x}" for i in res.state.trace if i in p.cfg.bb_addrs or i == res.state.trace[-1]])}')
        logging.info(call)
        for c in call:
            if c['caller'] == c['origin']:
                print('eth.sendTransaction({from:"0x%040x", data:"0x%s", to:"0x4000000000000000000000000000000000000000"%s, gasPrice:0})' % (c['origin'], c.get('payload', b'').hex(),", value:%d" % c['value'] if c.get('value', 0) else ''))
            else:
                print('eth.sendTransaction({from:"0x%040x", data:"0x%s", to:"0x%040x"%s, gasPrice:0})' % (
                    c['origin'], c.get('payload', b'').hex(), c['caller'],
                    ", value:%d" % c['value'] if c.get('value', 0) else ''))
        return True
    else:
        return False

def main():
    extracted_cfg = 0
    file_paths = list_files("new_contracts/")

    for file in file_paths:
        if run_combined_attack(file):
            extracted_cfg += 1
    logging.info(f'CFG extracted: {extracted_cfg}')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

    