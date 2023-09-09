# import pandas as pd

# def read_receipt(receipt, df):
#     for i in range(df.shape[0]):
#         row_params = df.loc[i]
#         if row_params.receipt_id == receipt:
#             print(row_params.name)

# df = pd.read_csv ("datasets/cosmetic_train.tsv", on_bad_lines='skip', sep='\t')
# # print(df)
# read_receipt(14118224448, df)


import pandas as pd

def calculate_percentage(count, total_count):
    return (count / total_count) * 100


df = pd.read_csv("datasets/cosmetic_train.tsv", on_bad_lines='skip', sep='\t')

df_grouped = df.groupby('receipt_id')['item_id'].apply(lambda x: ' '.join(map(str, x.unique()))).reset_index(name='id товаров у одного пользователя')


groups = {}

unique_item_ids = df['item_id'].unique()
for i, item_id in enumerate(unique_item_ids):

    group = df_grouped[df_grouped['id товаров у одного пользователя'].str.contains(str(item_id))]
    

    if not group.empty:
        if i not in groups:
            groups[i] = {'item_ids': set(), 'receipt_ids': [], 'different_items': {}, 'recommended_items': []}
        groups[i]['item_ids'].add(str(item_id))
        groups[i]['receipt_ids'].extend(list(group['receipt_id']))
        
        for receipt_id in group['receipt_id']:
            receipt_items = df[df['receipt_id'] == receipt_id]['item_id'].unique()
            for item in receipt_items:
                if item not in groups[i]['item_ids']:
                    if item in groups[i]['different_items']:
                        groups[i]['different_items'][item] += 1
                    else:
                        groups[i]['different_items'][item] = 1
        
        total_receipts = len(groups[i]['receipt_ids'])
        max_percentage = 0
        max_percentage_items = []
        for item, count in groups[i]['different_items'].items():
            percentage = calculate_percentage(count, total_receipts)
            if percentage > max_percentage:
                max_percentage = percentage
                max_percentage_items = [item]
            elif percentage == max_percentage:
                max_percentage_items.append(item)
        
        groups[i]['recommended_items'] = max_percentage_items

for group_id, data in groups.items():
    item_ids = ', '.join(data['item_ids'])
    receipt_ids = ', '.join(map(str, data['receipt_ids']))
    
    recommended_items_str = ', '.join(map(str, data['recommended_items']))
    
    print(f"Группа ({item_ids}): {receipt_ids} - рекомендую: {recommended_items_str}")
