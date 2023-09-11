# Gift Exchange Optimizer
An optimizer to create gift pairings. Takes into account:
* Excluding undesired pairings, e.g. pairing up partners, mortal enemies, etc
* Avoids recent repeat pairings as much as possible (exponential decay)
* Can accomodate added / dropped members

To use run exchange.py after filling out config.json. The fields are as follows:
* `currentExchange`: all members who will take part of this exchange. Other fields may include references to members not included here.
* `exclusionGroups`: a list of groups that cannot be paired with one another, e.g. partners, nuclear families, etc
* `previous`: a history of previous exchanges (`list[dict[str,str]]`, `{ giver: reciever }`).

Here is an example config.json:
```json
{
  "currentExchange": ["Alice", "Bob", "Charlie", "Denise", "Eve", "Frank"],
  "exclusionGroups": [
    ["Alice", "Bob"],
    ["Eve", "Frank"],
    ["Charlie", "Harriet"],
    ["Denise", "Gus"]
  ],
  "previous": [
    {
      "Denise": "Alice",
      "Charlie": "Eve",
      "Alice": "Frank",
      "Frank": "Charlie",
      "Eve": "Denise"
    },
    {
      "Denise": "Eve",
      "Charlie": "Bob",
      "Alice": "Charlie",
      "Bob": "Frank",
      "Frank": "Denise",
      "Eve": "Alice"
    },
    {
      "Denise": "Charlie",
      "Charlie": "Frank",
      "Alice": "Denise",
      "Bob": "Eve",
      "Frank": "Alice",
      "Eve": "Bob"
    },
    {
      "Denise": "Frank",
      "Charlie": "Alice",
      "Alice": "Eve",
      "Bob": "Denise",
      "Frank": "Bob",
      "Eve": "Charlie"
    }
  ]
}
```