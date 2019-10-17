import re
tempstr="Intel(R) Xeon(R) CPU E5-2680 v2 @ 2.80GHz"
print(re.search(r'(?<=CPU)',tempstr).group())
