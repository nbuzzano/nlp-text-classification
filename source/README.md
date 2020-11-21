In order to test this project, you should store the input data here with a folder structure like this:

```
|-source/
	|-dataset/
		|-train_set.csv
		|-test_set.csv
		|-
		|-train_set/
			|-612288.txt
			|-612289.txt
			|-etc
		|-
		|-test_set/
			|-112288.txt
			|-112289.txt
			|-etc
```

Where `train_set.csv` and `test_set.csv` are datasets with the following schema:
```
pk_id           int64
category       object
master_tree    object
file_type      object
```
1. **pk_id:** text id which can be found in the `train_set` or `test_set` folder.
1. **category:** text target.
1. **file_type:** file extension. This is not a really useful field.
1. **master_tree:** text origin source. This is not a really useful field.
