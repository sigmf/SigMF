# 
# Warning: this is not strict JSON, this is python to allow inline comment ...
#

{
	"global": {
		"core:type": "cf32",		# Mandatory
		"core:offset": 0,			# Optional if 0 ...
	},

	"capture": [ # Sorted list by sample_start
		# First one mandatory start at data start (either 0 or "offset", see global)
		{
			"sample_start": 0,				# Mandatory (and be 0)
			"core:samplerate": 10000000,	# 10 MHz
			"core:frequency": 950000000,	# 950 MHz
			"core:time": "2017-02-01T11:33:17,053240428+01:00",
			"uhd:gain": 34,					# App / Hw specific value
			# ...
		},
		# Only updated infos need to be present
		{
			"sample_start": 100000,			# Mandatory
			"core:frequency": 950000000,	# Now at 950 MHz
			"uhd:gain": 54,					# Now with more gain
			# ...
		},
	],

	"annotations": [ # Sorted list by sample_start
		{
			"sample_start": 100000,			# Mandatory
			"sample_length": 120000,		# Optional
			"core:comment": "Some textual comment about stuff happenning",
			"gsm:xxx": 111,					# Some application specific field
		},
	],
}

# - Global sections: Stuff valid for the entire file that can't change, ever
# - 'sample_length' of zero is invalid for capture_infos.

