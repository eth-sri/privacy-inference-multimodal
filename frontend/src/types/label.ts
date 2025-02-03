export interface Attributes {
  placeOfImage: AttributeDict;
  location: AttributeDict;
  sex: AttributeDict;
  age: AttributeDict;
  occupation: AttributeDict;
  placeOfBirth: AttributeDict;
  maritalStatus: AttributeDict;
  income: AttributeDict;
  educationLevel: AttributeDict;
  others: Record<string, AttributeDict>;
}

export interface AttributeDict {
  estimate: string;
  information_level: number;
  hardness: number;
  certainty: number;
}