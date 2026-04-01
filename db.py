import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, lognorm

conn = sqlite3.connect('sqlite3.db')
cursor = conn.cursor()

# cursor.execute('''SELECT name FROM PRAGMA_TABLE_INFO('mods')''') # Названия полей
# cursor.execute('''SELECT * FROM items''')
# cursor.execute('''SELECT * FROM mods''')
# cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name''') # чтобы посмотреть таблицы все в БД
# cursor.execute('''select id,name,hash,min,max from items JOIN mods ON items.Itemid = mods.Itemid where min-max <> 0 ''',) #чтобы посмотреть сколько модов прайсчекать
# cursor.execute('''select name,hash from items left join mods on items.Itemid = mods.id where name LIKE "%contract%" ''')
# cursor.execute('''select id,name,class,max-min as range from mods JOIN items ON mods.Itemid = items.Itemid where range <> 0 and range > 100 order by range asc ''',)
cursor.execute('''SELECT name, bo_price, minroll_price, maxroll_price from mods JOIN items on mods.Itemid = items.Itemid WHERE name LIKE "%Olroth's Resolve%" AND max-min <> 0''')






rows = cursor.fetchall()



# data = []
#
# for row in rows:
#     data.append((row[3]))

conn.close()

print(rows)

# # # 2. Calculate Mean and Standard Deviation
# # mu, sigma = np.mean(data), np.std(data)
# #
# # # 3. Plot Histogram & Theoretical Curve
# # plt.hist(data, bins=30, density=True, alpha=0.6, color='g', label='Data Histogram')
# # xmin, xmax = plt.xlim()
# # x = np.linspace(xmin, xmax, 100)
# # p = lognorm.pdf(x, mu, sigma)
# # plt.plot(x, p, 'k', linewidth=2, label='Normal PDF Curve')
# #
# # # 4. Formatting
# # plt.title(f"Normal Distribution: $\\mu={mu:.2f}$, $\\sigma={sigma:.2f}$")
# # plt.legend()
# # plt.show()
#
# # 2. Fit the lognormal distribution to the data
# # lognorm.fit() returns (shape, loc, scale) parameters.
# shape_fit, loc_fit, scale_fit = lognorm.fit(data, floc=0) # floc=0 fixes the location to 0
#
# print(f"Fitted shape (s): {shape_fit:.4f}")
# print(f"Fitted location (loc): {loc_fit:.4f}")
# print(f"Fitted scale (scale): {scale_fit:.4f}")
#
# # 3. Plot the histogram of the data
# fig, ax = plt.subplots(1, 1)
# # Use density=True to normalize the histogram so it can be compared with the PDF
# ax.hist(data, bins=100, density=True, alpha=0.6, color='g', label='Data Histogram')
#
# # Optional: You can also use a log scale for the x-axis, which is common for lognormal data
# # ax.set_xscale("log")
#
# # 4. Generate x values for the fitted PDF curve
# # Create an array of points for the curve to be smooth.
# # Use ppf (percent point function, inverse of cdf) to define reasonable plot limits.
# xmin, xmax = lognorm.ppf(0.01, shape_fit, loc=loc_fit, scale=scale_fit), \
#              lognorm.ppf(0.99, shape_fit, loc=loc_fit, scale=scale_fit)
# x = np.linspace(xmin, xmax, 1000)
#
# # 5. Calculate the PDF (Probability Density Function) using the fitted parameters
# pdf_fitted = lognorm.pdf(x, shape_fit, loc=loc_fit, scale=scale_fit)
#
# # 6. Plot the fitted PDF curve
# ax.plot(x, pdf_fitted, 'r-', lw=2, label='Fitted Lognormal PDF')
#
# # 7. Add labels, title, and a legend
# ax.set_xlabel('Value')
# ax.set_ylabel('Density')
# ax.set_title('Lognormal Distribution Fit to Data')
# ax.legend()
# plt.show()
