#更具交税金额，计算收入工资  20241224


def calculate_income_from_tax(tax_due):
    # 定义税率分级
    tax_brackets = [
        (36000, 0.03),
        (144000, 0.10),
        (300000, 0.20),
        (420000, 0.25),
        (960000, 0.35),
        (float('inf'), 0.45)  # > 960000
    ]

    total_tax = 0
    income = 0

    # 从最低税段开始反推
    for i in range(len(tax_brackets) - 1, -1, -1):
        # 当前税段的上限和税率
        bracket_limit, rate = tax_brackets[i]

        # 如果已累计税款大于当前税段的最大税额，跳过
        if total_tax + (bracket_limit - (tax_brackets[i-1][0] if i > 0 else 0)) * rate <= tax_due:
            tax_in_this_bracket = (bracket_limit - (tax_brackets[i-1][0] if i > 0 else 0)) * rate
            total_tax += tax_in_this_bracket
            income += (bracket_limit - (tax_brackets[i-1][0] if i > 0 else 0))
        else:
            break
    return income

# 示例
tax_due = 101080  # 假设给定的税款
income = calculate_income_from_tax(tax_due)
print(f"反推的收入为: {income}")
