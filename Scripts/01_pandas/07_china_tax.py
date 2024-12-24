#根据中国的tax，计算交税的金额 20241224

def calculate_tax(income):
    # 累进税率和区间定义（单位：元）
    tax_brackets = [
        (36000, 0.03),
        (144000, 0.10),
        (300000, 0.20),
        (420000, 0.25),
        (960000, 0.35),
        (float('inf'), 0.45)  # > 960000
    ]

    tax = 0  # 初始化应缴税金
    previous_limit = 0  # 前一个区间的上限

    for limit, rate in tax_brackets:
        if income > limit:
            tax += (limit - previous_limit) * rate  # 当前区间应缴税金
        else:
            tax += (income - previous_limit) * rate  # 剩余部分的税金
            break
        previous_limit = limit  # 更新前一个区间的上限

    return tax


if __name__ == "__main__":
    # 输入年收入
    annual_income = float(input("请输入您的年收入（元）："))
    tax = calculate_tax(annual_income)
    print(f"您的应缴个税金额为：{tax:.2f} 元")
