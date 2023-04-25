import xlwt
import xlrd


class WRExcel:

    @staticmethod
    def write_to_excel(infos, filename):
        work_book = xlwt.Workbook(encoding='utf-8')
        sheet = work_book.add_sheet('Sheet1')
        head = list(infos[0].keys())
        # 写表头
        for i in range(len(head)):
            # write(行数，列数，内容)
            sheet.write(0, i, head[i])
        # 写入内容，从第二行开始写
        rows = 1
        # 获取每一行数据
        for i in infos:
            # 写入每一列数据
            for j in range(len(head)):
                sheet.write(rows, j, i[head[j]])
            rows += 1
        work_book.save(filename)
        return "写入成功！"

    @staticmethod
    def read_excel(filename):
        wb = xlrd.open_workbook(filename)
        sheet = wb.sheet_by_name('Sheet1')
        all_data = list()
        for row in range(1, sheet.nrows):
            row_data = dict()
            for col in range(0, sheet.ncols):
                r = sheet.cell_value(0, col)
                c = sheet.cell_value(row, col)
                row_data[r] = c
            all_data.append(row_data)
        return all_data

infos = [
    {
        "ip": "1.1.1.1",
        "hostname": "host1",
        "os": "windows"
    },
    {
        "ip": "1.1.1.2",
        "hostname": "host2",
        "os": "linux"
    }
]

# filename = "./host.xls"
filename = "./host.xlsx"
WRExcel.write_to_excel(infos, "./host.xlsx")
print(WRExcel.read_excel("./host.xlsx"))
