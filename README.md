# Python_GUI_Menu

Python Generic GUI Menu Creator. This uses the **config.yml** to create a dynamic application.

````
icon: smallicon.png
logo: logo.png
menu_title: Title of Menu
menu_items:
  - name: Separator 1
    items:
      - name: Menu Item 1 from Separator 1
        command: ls -alF | grep travis
      - name: Menu Item 2 from Separator 1
        command: echo "This is a test"
  - name: Separator 2
    items:
      - name: Menu Item 1 from Separator 2
        command: echo "This is another test"
```


![](20250423172157.png)

![](20250423172429.png)

## Creating the Virtual Environment and Running the Menu

````
uv venv menu_venv --python=3.12
source menu_venv/bin/activate
uv pip install PyQt5 PyYaml
python menu.py
````