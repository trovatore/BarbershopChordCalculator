# Barbershop Chord Calculator
A specialized music theory tool for barbershop quartet singers and arrangers. Enter four notes to identify the chord and the functional role of each voice part.

The tool is currently tuned for **TTBB barbershop harmony**, following standard quartet engraving conventions:
* **Tenor & Lead:** Treble Clef (8vb) — Stems Up (Tenor), Stems Down (Lead).
* **Bari & Bass:** Bass Clef — Stems Up (Bari), Stems Down (Bass).

If you want to use it for SSAA or SATB, you could just pretend it's TTBB; the answers are the same except that open versus closed voicing might be different if you're using it for SATB.  If there is enough demand I will consider adding options for SATB or SSAA.  Or you are welcome to submit a pull request.


![screenshot](images/image.png)

## License
This application and its source code are released under the [MIT License](LICENSE).  There is no warranty of any kind, express or implied.

## Using the App
  * Select a Part: Click on a voice box (Bass, Bari, Lead, or Tenor) or use Tab (and Shift-Tab) to cycle through them.  The Right Arrow and Left Arrow will also cycle through the different voices.

  * Typing Notes: When a part is selected, simply type the letter (A-G) to change the note, possibly followed by an accidental (#, b, x, or bb), and then an octave number.

### Note Notation
  * Accidentals: Use b for flat, # for sharp, bb for double-flat, and x for double-sharp.
  * Octaves: Follow the letter with an octave number (e.g., G3, Bb3, Cx4).
  * Enharmonics: Click the Circular Arrow (↻) or press Enter to cycle through enharmonic spellings (e.g., changing a G# to an Ab).

### Controls
  * Arrow Keys (Up/Down): Move the selected note up or down by a semitone.
  * On-Screen Buttons: Use the arrows to adjust pitch or the ↻ button to re-spell the note.

## Installation
(This applies if you want to use the application from the source code.  If you are running the application on a hosted web platform you can ignore this section.)

### Prerequisites
You need **Python 3.10 or higher** installed on your computer.

### 1. Clone and Setup
1. Open your terminal (or Command Prompt/PowerShell on Windows) and run:

```bash
git clone https://github.com/trovatore/BarbershopChordCalculator.git
cd BarbershopChordCalculator
```
2. Create a Virtual Environment

  * In Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
  * In Windows:
```Powershell
python -m venv .venv
.venv\Scripts\activate
```
3. Install Dependencies
```
pip install -r requirements.txt
```

4. Run the App
```
python app.py
```
Once running, open your browser to: http://127.0.0.1:5001

## Development & Testing
To run the automated test suite and verify the music theory logic:
```
python -m unittest discover tests
```

To run the browser unit tests, with the app running, navagate to http://127.0.0.1:5001/tests/js.

## Contributing
Feedback and contributions are welcome!
For bugs, pain points during installation, or feature requests, please visit [the GitHub page for the project](https://github.com/trovatore/BarbershopChordCalculator), where you can open an Issue or join the Discussions.
Pull requests are encouraged.

