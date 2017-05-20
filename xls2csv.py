#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import xlrd
import unicodecsv

def xls2csv (xls_filename, csv_filename):
	print("Convert {} to {}...".format(xls_filename, csv_filename))
	wb = xlrd.open_workbook(xls_filename)
	sh = wb.sheet_by_index(0)

	fh = open(csv_filename,"wb")
	csv_out = unicodecsv.writer(fh, encoding='utf-8')

	for row_number in xrange (sh.nrows):
		csv_out.writerow(sh.row_values(row_number))

	fh.close()

if __name__ == "__main__":
	# usage: xls2csv from.xls to.xls
	if len(sys.argv) < 3:
		print("Usage: {} from.xls to.xls".format(sys.argv[0]))
		sys.exit()
	xls2csv(sys.argv[1], sys.argv[2])
