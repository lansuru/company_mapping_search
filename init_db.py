import pandas as pd
from app import db, Mapping, User

def load_mappings():
    DATABASE_FILE = 'database.txt'

    mapping_list = []
    with open(DATABASE_FILE, encoding='utf-8') as f:
        for line in f.readlines():
            items = line.strip().split(',')
            if len(items) == 2:
                mapping_list.append(items)
    # We assume the input list has been properly sorted and do not do any sorting here.
    return mapping_list

def add_mappings():
    mapping_list = load_mappings()
    for legacy, new in mapping_list:
        db.session.add(Mapping(legacy=legacy, new=new))
    db.session.commit()

    print('%d mappings added.' % len(mapping_list))

def add_users():
    # password_hash can be generated using Python:
    #
    # >>> from werkzeug.security import generate_password_hash
    # >>> generate_password_hash('Strong-Password') 
    #'pbkdf2:sha256:260000$NO8nEmbShCfkZpng$ef967230ed5ebc0cb5fec8a6075b71358d46089c6f75cadcaaa25d8fe6a662c7'

    fname = 'users.txt'
    df = pd.read_csv(fname)

    for _, row in df.iterrows():
        db.session.add(User(id=int(row.id), email=row.email, username=row.username, password_hash=row.password_hash))
    db.session.commit()

    print('%d users added.' % df.shape[0])

def main():
    db.drop_all()
    db.create_all()

    add_mappings()
    add_users()

if __name__ == "__main__":
    main()