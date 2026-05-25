import flet as ft
def main(page: ft.Page):
    page.add(ft.Text("Hello"))
if __name__ == "__main__":
    try:
        ft.run(target=main)
        print("ft.run exists")
    except AttributeError:
        print("ft.run does not exist")
