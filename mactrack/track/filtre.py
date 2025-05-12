import os
import shutil


def supprimer_petit(p):
    """
    Deletes subdirectories containing fewer than p PNG files in the specified directory, meaning the macrophages were tracked in less than .. math:`p` frames.
    
    Parameters:
        p (int): The threshold number of PNG files.
    """ 
    dossier_principal = "output/list_track"
    for root, dirs, files in os.walk(dossier_principal):
        for dir in dirs:
            chemin_sous_dossier = os.path.join(root, dir)
            fichiers_png = [
                f for f in os.listdir(chemin_sous_dossier) if f.endswith(".png")
            ]
            if len(fichiers_png) <= p:
                shutil.rmtree(chemin_sous_dossier)
                print(f"Sous-dossier supprimé : {chemin_sous_dossier}")
