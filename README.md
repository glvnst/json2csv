# json2csv

Do you have a JSON file, [like the staticsitegenerators.net list of static site generator software](http://staticsitegenerators.net/list.json)? Do you want to convert it to CSV and slice/dice it in a spreadsheet?

- Q: "Now I can?"
- A: Possibly "yes," my friend.

##  Usage

	usage: json2csv [-h] [-w] [-d] inputfile [inputfile ...]
	
	Create a CVS file from a JSON file. The input files must contain an array of
	objects with uniform keys. Output will be written to the current working
	directory. For example for the input file '/something/thing.json' we create
	'./thing.csv'. By default existing files will not be overwritten.
	
	positional arguments:
	  inputfile        Input JSON file(s)
	
	optional arguments:
	  -h, --help       show this help message and exit
	  -w, --overwrite  Overwrite the output file(s) if they exist
	  -d, --debug      Print debugging output instead of generating CSV files
  
## Support Information

This program is provided without technical support. For more information see the project home page at <http://example.com/>

## License

This program is distributed WITHOUT ANY WARRANTY under terms described in the file LICENSE.txt.
