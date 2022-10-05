from itertools import chain, combinations

tags_list_share = ['HIV+', 'PARTNER_HIV+', 'PWID_SHARE', 'PWID_SHARE', 'MSM', 'NO_VACCINE_B', 'MIGRANT',
              'NO_TB_SCREENING']


tags_list_noShare = ['HIV+', 'PARTNER_HIV+', 'PWID_NO_SHARE', 'MSM', 'NO_VACCINE_B', 'MIGRANT',
              'NO_TB_SCREENING']

tags_list_share_noHIV = ['PWID_SHARE', 'MSM', 'NO_VACCINE_B', 'MIGRANT',
              'NO_TB_SCREENING']


tags_list_noShare_noHIV = ['PWID_NO_SHARE', 'MSM', 'NO_VACCINE_B', 'MIGRANT',
              'NO_TB_SCREENING']

def all_subsets(items):
    return chain(*map(lambda x: combinations(items, x), range(0, len(items)+1)))

for subset in all_subsets(tags_list_share):
    print(subset)

for subset in all_subsets(tags_list_noShare):
    print(subset)


for subset in all_subsets(tags_list_share_noHIV):
    print(subset)

for subset in all_subsets(tags_list_noShare_noHIV):
    print(subset)