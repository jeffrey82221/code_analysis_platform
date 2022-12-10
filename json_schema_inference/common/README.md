# `Parametric Schema Inference for Massive JSON Datasets`

# How the paper define the json schema ? 

- Atomic Values (aka. `Simple`):
	- numbers (aka. `int`, `float`)
	- strings (aka. `str`)
	- booleans (aka. `bool`)
	- null (aka. `None`)
- Complex Values:
	- record: unordered sets of key/value paris (aka. `Dict`)
	- array: ordered list of values (aka. `List`)

# Additional Union Object for expersiveness

union are represented by `+` and `*` symbol:
- Union of two types: `type1 + type2`. (aka. `Union({type1, type2})`
- Union of a non-null type and a null value: `type1 + null`. (aka. `Optional(non_null_type)`

# How the paper merge schemas? 

- Two atomic types: type1 | type2 -> type1 + type2
- Two record types: missing keys are documented as Optional. 


# TODO:
- [ ] Enable the selection of kind equivalence and label equivalence:
	- [ ] kind equivalence: 
		-  [ ] Turn on `DynamicDict`
		-  [ ] Allow `DynamicDict` to be represented with marking of whether a field is optional (missing some times) or not. 
	-  [ ] label equivalence:
		-  [ ] Turn off `DynamicDict` (Dict with different labels should be merged into `Union` of Dict(s))
- [ ] Construction of UniformDict should be optional, too. 
- [ ] Try to imitate the json schema of the paper
	- [ ] `Simple` -> `Atomic`
	- [ ] `Dict` -> `Record`
	- [ ] `List` -> `Array`
