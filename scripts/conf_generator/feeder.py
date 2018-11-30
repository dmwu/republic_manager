import json
import pprint


def gen_feeder(feeder_l):
    ret = []
    for feeder in feeder_l:
        for port in range(feeder["starting"], feeder["starting"] + feeder["num"]):
            ret.append({"port": port})
    return ret


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=2)
    results = gen_helper(5, 190)
    pp.pprint(results)

    with open('helper.json', 'w') as outfile:
        json.dump(results, outfile, sort_keys=True, indent=2, ensure_ascii=False)
