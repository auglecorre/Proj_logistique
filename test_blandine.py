class Lego :

    def __init__(self, taille, couleur):
        self.taille = taille
        self.couleur = couleur
        self.modèle = (taille*2, couleur)

    def __repr__(self) -> str:
        print("ce lego est de couleur ")



Lego(4, 'bleue')
Lego(6, 'rouge')

print(Lego(4, 'bleue').modèle)


{1: ['Source', '2', 'Sink'],
 2: ['Source', '31', 'Sink'],
 3: ['Source', '1', 'Sink'],
 4: ['Source', '23', '11', '12', '16', 'Sink'],
 5: ['Source', '14', '15', '6', '38', 'Sink'],
 6: ['Source', '34', '33', 'Sink'],
 7: ['Source', '40', '32', 'Sink'],
 8: ['Source', '8', '30', '5', 'Sink']}
