# -*- coding: utf-8 -*-
"""
main.py —— 菜单式命令行程序（ST-5.5）
启动时打印连接状态与各集合文档总数；菜单覆盖检索/统计/更新/删除；
变更后打印受影响文档数；查询无结果给出提示；退出前关闭连接。
"""
import mongodb_connect
import book_manager
import reader_manager
import borrow_manager
import stat_manager


def show_header():
    ok, ver = mongodb_connect.server_status()
    print("=" * 56)
    print("  图书情报检索与统计平台")
    print("=" * 56)
    print(f"  数据库连接: {'正常' if ok else '失败'}  MongoDB v{ver}")
    print(f"  图书 books     : {book_manager.count()} 条")
    print(f"  读者 readers   : {reader_manager.count()} 条")
    print(f"  借阅 borrow_logs: {borrow_manager.count()} 条")
    print("=" * 56)


def menu():
    print("""
  ── 功能菜单 ──
  1. 按条件检索图书（书名/作者/ISBN）
  2. 图书评分排行 Top5
  3. 分类统计报表（库存/均价/数量）
  4. 借阅趋势分析（按年份）
  5. 畅销榜（借阅次数 Top5）
  6. 读者学院 / 等级分布
  7. 新增图书
  8. 借阅登记
  9. 归还处理
  0. 退出
""")


def empty_hint():
    print("  （查询无结果）")


def main():
    show_header()
    while True:
        menu()
        choice = input("请输入功能编号: ").strip()

        if choice == "1":
            kw = input("输入关键字（书名/作者/ISBN，直接回车=全部）: ").strip()
            q = {} if not kw else {"title": {"$regex": kw}}
            rows = book_manager.find_books(q, {"title": 1, "author": 1, "price": 1, "stock": 1, "_id": 0})
            if not rows:
                empty_hint()
            for r in rows:
                print("   ", r)

        elif choice == "2":
            rows = book_manager.rating_rank(5)
            if not rows:
                empty_hint()
            for i, r in enumerate(rows, 1):
                print(f"   {i}. {r['title']}  评分={r['rating']}  价格={r['price']}")

        elif choice == "3":
            rows = stat_manager.category_stat()
            if not rows:
                empty_hint()
            for r in rows:
                print(f"   类别={r['_id']:6s} 图书数={r['book_count']:2d} 库存总量={r['total_stock']:3d} 平均价={round(r['avg_price'],1)}")

        elif choice == "4":
            rows = stat_manager.borrow_trend()
            if not rows:
                empty_hint()
            for r in rows:
                print(f"   {r['_id']}  借阅量={r['total']}")

        elif choice == "5":
            rows = stat_manager.bestseller(5)
            if not rows:
                empty_hint()
            for i, r in enumerate(rows, 1):
                print(f"   {i}. {r['title']}  累计借阅={r['borrow_count']}")

        elif choice == "6":
            print("   学院分布:")
            for r in reader_manager.college_distribution():
                print(f"     {r['_id']}: {r['n']} 人")
            print("   等级分布:")
            for r in reader_manager.level_distribution():
                print(f"     {r['_id']}: {r['n']} 人")

        elif choice == "7":
            isbn = input("ISBN: ").strip()
            title = input("书名: ").strip()
            author = input("作者: ").strip()
            price = float(input("价格: ").strip())
            stock = int(input("库存: ").strip())
            bid = book_manager.add_book({
                "isbn": isbn, "title": title, "author": author,
                "price": price, "stock": stock, "rating": 0.0,
                "category": "未分类", "tags": [], "borrow_count": 0})
            print(f"   新增成功，受影响文档数=1，_id={bid}")

        elif choice == "8":
            card = input("借阅证号: ").strip()
            isbn = input("图书ISBN: ").strip()
            bid = borrow_manager.borrow_book(card, isbn)
            print(f"   借阅登记成功，受影响文档数=1，_id={bid}")

        elif choice == "9":
            card = input("借阅证号: ").strip()
            isbn = input("图书ISBN: ").strip()
            n = borrow_manager.return_book(card, isbn)
            print(f"   归还处理完成，受影响文档数={n}")

        elif choice == "0":
            mongodb_connect.close()
            print("   数据库连接已关闭，再见！")
            break
        else:
            print("   无效编号，请重新输入。")


if __name__ == "__main__":
    main()
