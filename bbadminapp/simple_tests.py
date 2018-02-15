total_pages = 245
current_page = 245
data_set = 10
total_records = 2447
pages_to_display = 8
display_window = []

for i in range(1, total_pages - pages_to_display, pages_to_display):
    display_window += [[j for j in range(i, i + pages_to_display)]]



from pprint import pprint
pprint(display_window)
# print(current_page % pages_to_display)

