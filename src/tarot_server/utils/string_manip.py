def count_any_occurrence(s: str, string: str) -> int:
	"""This function is used to count the number of occurrences of any
	character in a given string (string), inside another string (s)."""

	return sum([s.count(char) for char in string])
