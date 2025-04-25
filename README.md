# Pirate User Searcher GUI

A GUI application for searching The Pirate Bay by usernames and terms, built with CustomTkinter and Pmw. It saves search data to CSV, sorts results, and displays clickable torrent links.
Multiple users and terms can be targeted and sorted at once and relevant links from the torrent's page are also displayed (e.g., screenshots). 

## Features

- Search torrents by usernames and search terms.
- Save and load search data to/from CSV files.
- Sort results by date, size, seeders and more.
- Display clickable Pirate Bay URLs, magnet links, and relevant URLs (e.g., screenshots).
- Modern interface with CustomTkinter, scalable to different screen sizes.
- Tooltips for navigation using Pmw.Balloon.

## Prerequisites

- **Python 3.8+**: Ensure Python is installed with `tcl` and `tk` (usually included by default).
- Install dependencies from `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```
- **PyInstaller**: Required for building the executable (optional for running):
  ```bash
  pip install pyinstaller
  ```

## Project Structure

- `PirateUserSearcherGUI.py`: Main application script.
- `Resources/`: Directory containing images (`storm.jpg`, `pirate.png`, etc.) and theme (`harle.json`).
- `PirateUserSearcherGUI.spec`: PyInstaller specification file for building the executable.
- `requirements.txt`: Lists all Python dependencies required to run the application.

## Running the Application

To run the application directly (without building an executable):
1. Clone the repository:
   ```bash
   git clone https://github.com/AutomationsByAuto/PirateUserSearcherGUI.git
   cd PirateUserSearcherGUI
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure all resources are in the `Resources/` directory (see below).
4. Run the script:
   ```bash
   python PirateUserSearcherGUI.py
   ```

## Building the Executable

To create a standalone executable, use PyInstaller with the provided `PirateUserSearcherGUI.spec` file. You must customize the `.spec` file to include the path to your `Pmw` library and match your system’s file paths for Python libraries and the `Resources/` folder.

### Step 1: Prepare Resources

1. Ensure the `Resources/` directory is in the project root.
2. Verify the following files are in `Resources/`:
   - Images: `storm.jpg`, `pirate.png`, `pirate.ico`, `home.png`, `form.png`, `delete.png`, `search.png`, `back.png`, `coffee.png`, `selected.png`, `unselected.png`
   - Theme: `harle.json`
3. Confirm file names match those referenced in `PirateUserSearcherGUI.py`.

### Step 2: Customize the `.spec` File

The `PirateUserSearcherGUI.spec` file specifies paths to resources and Python libraries. You must update the `datas` section to include the path to your `Pmw` library and other system-specific paths.

1. **Locate Your Python Environment and Pmw Path**:
   - Find your Python installation’s `site-packages` and `tcl`/`tk` directories. Examples:
     - **Windows**: `C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python313\Lib\site-packages`, `C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python313\tcl\tcl8.6`, `C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python313\tcl\tk8.6`
     - **Linux**: `/usr/lib/python3.9/site-packages`, `/usr/lib/tcl8.6`, `/usr/lib/tk8.6`
     - **macOS**: `/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages`
   - Locate the `Pmw` library in your `site-packages` directory (e.g., `<path-to-your-python>/Lib/site-packages/Pmw`).
   - Use Python to find `site-packages`:
     ```python
     python -c "import site; print(site.getsitepackages())"
     ```

2. **Update the `.spec` File**:
   - Open `PirateUserSearcherGUI.spec` and modify the `datas` section to include the `Pmw` path and other resources. Below is a sample `.spec` with placeholders:
     ```python
     a = Analysis(
         ['PirateUserSearcherGUI.py'],
         pathex=[],
         binaries=[],
         datas=[
             ('<path-to-your-python>/Lib/site-packages/Pmw', 'Pmw'),
             ('<path-to-your-python>/tcl/tcl8.6', 'tcl'),
             ('<path-to-your-python>/tcl/tk8.6', 'tk'),
             ('Resources/storm.jpg', 'Resources'),
             ('Resources/pirate.png', 'Resources'),
             ('Resources/home.png', 'Resources'),
             ('Resources/form.png', 'Resources'),
             ('Resources/delete.png', 'Resources'),
             ('Resources/search.png', 'Resources'),
             ('Resources/back.png', 'Resources'),
             ('Resources/coffee.png', 'Resources'),
             ('Resources/selected.png', 'Resources'),
             ('Resources/unselected.png', 'Resources'),
             ('Resources/harle.json', 'Resources'),
             ('Resources/pirate.ico', 'Resources')
         ],
         hiddenimports=['Pmw', 'Pmw.Balloon', 'tkinter', 'customtkinter', 'Pmw.Color', 'Pmw.MessageDialog', 'Pmw.ScrolledText', 'PIL', 'PIL.Image', 'PIL.ImageTk'],
         hookspath=[],
         hooksconfig={},
         runtime_hooks=[],
         excludes=[],
         noarchive=False,
         optimize=0,
     )
     pyz = PYZ(a.pure)
     exe = EXE(
         pyz,
         a.scripts,
         [],
         exclude_binaries=True,
         name='PirateUserSearcherGUI',
         debug=False,
         bootloader_ignore_signals=False,
         strip=False,
         upx=True,
         console=True,  # Set to False for no console window
         disable_windowed_traceback=False,
         argv_emulation=False,
         target_arch=None,
         codesign_identity=None,
         entitlements_file=None,
     )
     coll = COLLECT(
         exe,
         a.binaries,
         a.datas,
         strip=False,
         upx=True,
         upx_exclude=[],
         name='PirateUserSearcherGUI',
     )
     ```
   - Replace `<path-to-your-python>` with your Python installation path (e.g., `C:/Users/<YourUsername>/AppData/Local/Programs/Python/Python313`).
   - Ensure the `Pmw` path points to the `Pmw` directory in your `site-packages` (e.g., `C:/Users/<YourUsername>/AppData/Local/Programs/Python/Python313/Lib/site-packages/Pmw`).
   - Ensure `Resources/` paths point to the project’s `Resources/` directory (e.g., `Resources/storm.jpg` assumes the file is in `project/Resources/`).
   - The `Resources` destination in `datas` (e.g., `('Resources/harle.json', 'Resources')`) ensures files are placed in a `Resources/` subfolder in the built executable, matching the script’s `resource_path("Resources/<filename>")` usage.

3. **Verify Resources**:
   - Confirm all listed files exist in the project’s `Resources/` directory.
   - Missing files will cause `FileNotFoundError` at runtime.

### Step 3: Build the Executable

1. Run PyInstaller with the customized `.spec`:
   ```bash
   pyinstaller PirateUserSearcherGUI.spec
   ```
2. Find the executable in `dist/PirateUserSearcherGUI/`.

### Step 4: Test the Executable

Run the executable:
```bash
# Windows
.\dist\PirateUserSearcherGUI\PirateUserSearcherGUI.exe

# Linux/macOS
./dist/PirateUserSearcherGUI/PirateUserSearcherGUI
```
- Check for errors in the console (if `console=True` in `.spec`).
- Verify the GUI loads with the custom theme (`harle.json`), background (`storm.jpg`), button icons, and tooltips.

## Notes

- **Resources Folder**: The `Resources/` folder is critical. It contains all images and the `harle.json` theme file. Ensure it is included in the repository and placed in the project root.
- **Why Customize the `.spec`?**: The `.spec` file tells PyInstaller where to find resources and libraries, including `Pmw`. Paths are system-specific, so users must update them. The script uses a `resource_path` function to locate files in PyInstaller’s `_MEIPASS` directory, requiring the `.spec` to bundle files into a `Resources/` subfolder.
- **Single-File Executable**: For a single `.exe`, modify the `.spec`:
  ```python
  exe = EXE(
      pyz,
      a.scripts,
      a.binaries,
      a.datas,
      name='PirateUserSearcherGUI',
      debug=False,
      bootloader_ignore_signals=False,
      strip=False,
      upx=True,
      console=False,
  )
  ```
  Remove the `coll = COLLECT` block and set `exclude_binaries=False`.
- **Fallback Theme**: If `harle.json` causes issues, edit `PirateUserSearcherGUI.py`:
  ```python
  # Replace:
  ctk.set_default_color_theme(resource_path("Resources/harle.json"))
  # With:
  ctk.set_default_color_theme("blue")
  ```
  Then rebuild.

## Troubleshooting

- **FileNotFoundError**: Ensure all resources are in `Resources/` and listed in `datas` with destination `'Resources'`. Check paths in `.spec`, including the `Pmw` path.
- **Pmw/Tkinter Errors**: Verify the `Pmw`, `tcl8.6`, and `tk8.6` paths in the `.spec` match your Python installation.
- **Console Output**: Keep `console=True` in `.spec` to see errors. Check `dist/PirateUserSearcherGUI/` for logs.
- **Logging**: Add to `PirateUserSearcherGUI.py` for debugging:
  ```python
  import logging
  logging.basicConfig(filename='app.log', level=logging.DEBUG)
  ```
  Check `app.log` in the executable directory.
- **Build Fails**: Verify dependencies (`pip install -r requirements.txt`) and `.spec` paths, especially the `Pmw` path in `datas`.

## Usage

1. Launch the application or executable.
2. On the landing page:
   - Start a fresh search or load a previous dataset (CSV).
3. In the search form:
   - Enter a Pirate Bay URL or proxy.
   - Input usernames and search terms (comma-separated).
   - Click "Check" to verify the URL, then "Search" to find torrents.
4. View results:
   - Sort by newest, oldest, largest, smallest, seeded, or random.
   - Click magnet links or URLs to open in your browser.
   - Refine results by filtering titles.
5. Save data:
   - Click "New Save" for a new CSV or "Overwrite" to update an existing one.

## Contributing

- Report issues or submit pull requests on GitHub.
- When adding resources, update `PirateUserSearcherGUI.spec` and document changes.
- Test builds on your system and include your `.spec` in issue reports.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

## Motivation

Having searched for such a tool online and being unable to find one I decided to make it my next project. 

## Disclaimer

This application interacts with The Pirate Bay. Use it responsibly and in compliance with applicable laws. The developers are not responsible for misuse.

## Contact
Ray Pitcher - mass.automation.solutions@gmail.com

Aspiring Automation Engineer | Open to feedback and collaboration!
