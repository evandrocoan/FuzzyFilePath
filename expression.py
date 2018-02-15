import re
import sublime
import FuzzyFilePath.common.settings as settings
import FuzzyFilePath.common.selection as Selection
import FuzzyFilePath.common.verbose as logger

ID = "Expression"

NEEDLE_SEPARATOR = ">\"\'\(\)\{\}"
NEEDLE_SEPARATOR_BEFORE = "\"\'\(\{"
NEEDLE_SEPARATOR_AFTER = "^\"\'\)\}"
NEEDLE_CHARACTERS = "\.A-Za-z0-9\-\_$"
NEEDLE_INVALID_CHARACTERS = "\"\'\)=\:\(<>\n\{\}"
DELIMITER = "\s\:\(\[\=\{"

def get_context(view):
	error = False
	valid = True
	valid_needle = True
	position = Selection.get_position(view)

	# print("position: `%s`" % position)

	# regions
	word_region = view.word(position)
	line_region = view.line(position)
	pre_region = sublime.Region(line_region.a, word_region.a)
	post_region = sublime.Region(word_region.b, line_region.b)

	# print("word_region: `%s`" % word_region)
	# print("line_region: `%s`" % line_region)
	# print("pre_region:  `%s`" % pre_region)
	# print("post_region: `%s`" % post_region)

	# text
	line = view.substr(line_region)
	word = view.substr(word_region)
	pre = view.substr(pre_region)
	post = view.substr(post_region)

	# print("line: `%s`" % line)
	# print("word: `%s`" % word)
	# print("pre:  `%s`" % pre)
	# print("post: `%s`" % post)

	error = re.search("[" + NEEDLE_INVALID_CHARACTERS + "]", word)
	needle_region = view.word(position)

	# print("error: `%s`" % error)
	# print("needle_region: `%s`" % needle_region)

	# grab everything in 'separators'
	needle = ""
	separator = False
	pre_match = ""
	# search for a separator before current word, i.e. <">path/to/<position>
	pre_quotes = re.search("(["+NEEDLE_SEPARATOR_BEFORE+"])([^"+NEEDLE_SEPARATOR+"]*)$", pre)

	# print("pre_quotes 1: `%s`" % pre_quotes)

	if pre_quotes:
		needle += pre_quotes.group(2) + word
		separator = pre_quotes.group(1)
		pre_match = pre_quotes.group(2)
		needle_region.a -= len(pre_quotes.group(2))
	else:
		# use whitespace as separator
		pre_quotes = re.search("(\s)([^"+NEEDLE_SEPARATOR+"\s]*)$", pre)
		# print("pre_quotes 2: `%s`" % pre_quotes)

		if pre_quotes:
			needle = pre_quotes.group(2) + word
			separator = pre_quotes.group(1)
			pre_match = pre_quotes.group(2)
			needle_region.a -= len(pre_quotes.group(2))

	# print("needle:        `%s`" % needle)
	# print("separator:     `%s`" % separator)
	# print("pre_match:     `%s`" % pre_match)
	# print("needle_region: `%s`" % needle_region)

	if pre_quotes:
		post_quotes = re.search("^(["+NEEDLE_SEPARATOR_AFTER+"]*)", post)
		if post_quotes:
			needle += post_quotes.group(1)
			needle_region.b += len(post_quotes.group(1))
		else:
			logger.verbose(ID, "no post quotes found => invalid")
			valid = False
		# print("post_quotes:   `%s`" % post_quotes)
	elif not re.search("["+NEEDLE_INVALID_CHARACTERS+"]", needle):
		needle = pre + word
		needle_region.a = pre_region.a
	else:
		needle = word

	# print("pre_quotes 3:  `%s`" % pre_quotes)
	# print("needle:        `%s`" % needle)
	# print("needle_region: `%s`" % needle_region)
	# print("valid:         `%s`" % valid)

	# grab prefix
	prefix_region = sublime.Region(line_region.a, pre_region.b - len(pre_match) - 1)
	prefix_line = view.substr(prefix_region)
	# print("prefix line", prefix_line)

	# print("prefix_line:   `%s`" % prefix_line)
	# print("prefix_region: `%s`" % prefix_region)

	#define? (["...", "..."]) -> before?
	# before: ABC =:([
	prefix = re.search("\s*(["+NEEDLE_CHARACTERS+"]+)["+DELIMITER+"]*$", prefix_line)

	# print("prefix 1: `%s`" % prefix)

	if prefix is None:
		# validate array, like define(["...", ".CURSOR."])
		prefix = re.search("^\s*(["+NEEDLE_CHARACTERS+"]+)["+DELIMITER+"]+", prefix_line)

	# print("prefix 2: `%s`" % prefix)

	if prefix:
		# print("prefix:", prefix.group(1))
		prefix = prefix.group(1)

	# print("prefix 3: `%s`" % prefix)

	tag = re.search("<\s*(["+NEEDLE_CHARACTERS+"]*)\s*[^>]*$", prefix_line)
	# print("tag 1: `%s`" % tag)

	if tag:
		tag = tag.group(1)
		# print("tag:", tag)

	propertyName = re.search("[\s\"\'']*(["+NEEDLE_CHARACTERS+"]*)[\s\"\']*\:[^\:]*$", prefix_line)

	# print("tag 2: `%s`" % tag)
	# print("propertyName 1: `%s`" % propertyName)

	if propertyName:
		propertyName = propertyName.group(1)

	# print("propertyName 2: `%s`" % propertyName)

	if separator is False:
		logger.verbose(ID, "separator undefined => invalid", needle)
		valid_needle = False
		valid = False
	elif re.search("["+NEEDLE_INVALID_CHARACTERS+"]", needle):
		logger.verbose(ID, "invalid characters in needle => invalid", needle)
		valid_needle = False
		valid = False
	elif prefix is None and separator.strip() == "":
		logger.verbose(ID, "prefix undefined => invalid", needle)
		valid = False

	# print("valid: `%s`" % valid)
	# print("valid_needle: `%s`" % valid_needle)

	results = {
		"is_valid": valid,
		"valid_needle": valid_needle,
		"needle": needle,
		"prefix": prefix,
		"tagName": tag,
		"style": propertyName,
		"region": needle_region,
		"word": word,
		# really do not use any of this
		"error": error
	}

	# print("results: `%s`" % results)
	return results

def check_trigger(trigger, expression):
	# returns True if the expression statements match the trigger
	for statement in set(settings.get("trigger_statements")).intersection(trigger):
		values = trigger.get(statement)
		# statement values may be None (or any other value...)
		if type(values) is list and not expression.get(statement) in values:
			return False
		# validate other value by comparison
		# elif not values == expression.get(statement):
		# 	return False

	return True

def find_trigger(expression, scope, triggers):
	for trigger in triggers:
		# if the trigger is defined for the current scope
		# REQUIRED? scope = properties.get("scope").replace("//", "")
		if re.search(trigger["scope"], scope):
			# validate its statements on the current context
			if check_trigger(trigger, expression):
				return trigger

	return False

def get_rule(view):

	selection = view.sel()[0]
	position = selection.begin()
	word_region = view.word(position)

	current_scope = view.scope_name(word_region.a)
	context = get_context(view)
	rule = find_rule(context, current_scope)

	return [rule, context] if rule else False
