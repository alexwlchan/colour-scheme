# colour-scheme

## Steps

1.  Get a new copy of the CSS files from the `alexwlchan.net` repo:

    ```console
    $ python3 vendor_css_files.py
    ```

2.  Generate a new set of theme files based on those colours:

    ```console
    $ python3 generate_palette_files.py
    ```

## TextMate

1.  Select the **Bundles** menu bar item, then select **Edit Bundles…**.

2.  Select the **Themes** bundle, then the **Themes** sub-item.

3.  Right-click on one of the theme files, and select **Show in Finder**.

4.  Open the `.tmTheme` file in TextEdit, and replace the `author`, `name`, and `semanticClass` values.

5.  Return to the TextMate bundle editor, and copy/paste the theme file from `out` into the editor.

6.  Restart TextMate.
