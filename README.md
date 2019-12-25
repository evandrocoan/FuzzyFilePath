# [FuzzyFilePath](https://github.com/sagold/FuzzyFilePath)

__Sublime Text Plugin__

Fuzzy search and insert filenames inside your current project directory. Highly customizable.

<img src="https://raw.githubusercontent.com/sagold/FuzzyFilePath/develop/FuzzyFilePathDemo.gif" />
<br />
<em style="display: block; text-align: right;">Basic settings support Javascript, HTML, CSS, PHP and glsl, but may be
adjusted for most languages</em>


## Installation

### By Package Control

1. Download & Install **`Sublime Text 3`** (https://www.sublimetext.com/3)
1. Go to the menu **`Tools -> Install Package Control`**, then,
   wait few seconds until the installation finishes up
1. Now,
   Go to the menu **`Preferences -> Package Control`**
1. Type **`Add Channel`** on the opened quick panel and press <kbd>Enter</kbd>
1. Then,
   input the following address and press <kbd>Enter</kbd>
   ```
   https://raw.githubusercontent.com/evandrocoan/StudioChannel/master/channel.json
   ```
1. Go to the menu **`Tools -> Command Palette...
   (Ctrl+Shift+P)`**
1. Type **`Preferences:
   Package Control Settings – User`** on the opened quick panel and press <kbd>Enter</kbd>
1. Then,
   find the following setting on your **`Package Control.sublime-settings`** file:
   ```js
       "channels":
       [
           "https://packagecontrol.io/channel_v3.json",
           "https://raw.githubusercontent.com/evandrocoan/StudioChannel/master/channel.json",
       ],
   ```
1. And,
   change it to the following, i.e.,
   put the **`https://raw.githubusercontent...`** line as first:
   ```js
       "channels":
       [
           "https://raw.githubusercontent.com/evandrocoan/StudioChannel/master/channel.json",
           "https://packagecontrol.io/channel_v3.json",
       ],
   ```
   * The **`https://raw.githubusercontent...`** line must to be added before the **`https://packagecontrol.io...`** one, otherwise,
     you will not install this forked version of the package,
     but the original available on the Package Control default channel **`https://packagecontrol.io...`**
1. Now,
   go to the menu **`Preferences -> Package Control`**
1. Type **`Install Package`** on the opened quick panel and press <kbd>Enter</kbd>
1. Then,
search for **`FuzzyFilePath`** and press <kbd>Enter</kbd>

See also:

1. [ITE - Integrated Toolset Environment](https://github.com/evandrocoan/ITE)
1. [Package control docs](https://packagecontrol.io/docs/usage) for details.


## <a name="usage">Usage</a>

**Filepaths will be suggested if there is a matching
[trigger](https://github.com/sagold/FuzzyFilePath/wiki/Settings#trigger) for the current context** and its property
_auto_ is set to _true_. For a matching [trigger](https://github.com/sagold/FuzzyFilePath/wiki/Settings#trigger),
filepath completions may be forced (ignoring _auto_ property) by the following shorcuts:

- <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Space</kbd> inserts filepaths relative, overriding possible settings
- <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>Space</kbd> inserts filepaths absolute, overriding possible settings

The current string may modify the suggested filepaths by the following rules:

- `word` suggests all matching files by the type (relative or absolute) as specified in the matched rule
- `./` suggests matching files within the current directory and inserts selection relative
- `../` suggests all matching files and inserts selection relative
- `/folder` suggests all matching files and insert selection absolute

FuzzyFilePath is disabled for single files or files outside the opened folder.


### Open File

Use <kbd>Alt</kbd>+<kbd>Enter</kbd> to open the file under cursor


### Configure Completion Panel

Ensure you have [autocompletion activated for Sublime](https://www.granneman.com/webdev/editors/sublime-text/top-features-of-sublime-text/auto-completion-in-sublime-text/). In those cases, where the autocompletion panel is still
not opened (for any type of completions), you may extend `auto_complete_triggers` to add special rules for the
completion panel to show up. i.e. enabling autocompletion for latex `\input{"path/to/asset"}`, you could add:

```json
"auto_complete_triggers":
[
	{
		"characters": "abcdefghijklmnopqrstuvwxyz",
		"selector": "text.tex.latex"
	}
]
```

or enabling html completion for `<script src="path/to/script">`

```json
"auto_complete_triggers":
[
	{
		"characters": "abcdefghijklmnopqrstuvwxyz",
		"selector": "string.quoted.double.html"
	}
]
```


### Special Characters

If your projects contains filenames with special characters, consider modifying Sublime Texts `word_separators`.

i.e. in AngularJs filenames may start with `$`. In _Sublime Text | Preferences | Settings - User_ redeclare word
separators, removing `$`:
```js
	"word_separators": "./\\()\"'-:,.;<>~!@#%^&*|+=[]{}`~?"
```


## Customization

For further details about troubleshooting, customization, settings and keybindings please
[refer to the Wiki](https://github.com/sagold/FuzzyFilePath/wiki)

Trying to integrate other languages? See the
[auto complete Python package tutorial](https://github.com/sagold/FuzzyFilePath/wiki/Tutorial:-Add-support-for-python-packages)


#### Related Plugins

##### [AutoFileName](https://github.com/BoundInCode/AutoFileName)

- uses file discovery based on current directory instead of fuzzy search
- adds properties for images in autocompletion description


___
## License

All files in this repository are released under GNU General Public License v3.0
or the latest version available on http://www.gnu.org/licenses/gpl.html

1. The [LICENSE](LICENSE) file for the GPL v3.0 license
1. The website https://www.gnu.org/licenses/gpl-3.0.en.html

For more information.




