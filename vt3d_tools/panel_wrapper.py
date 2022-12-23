import numpy as np

class Plane:
    def __init__(self,p0,p1,p2):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.n = np.cross((p1-p0),(p2-p0))
        norm=np.linalg.norm(self.n)
        if norm == 0 :
            print("Error: invalid norm vector",flush=True)
            sys.exit(1)
        self.n = self.n / norm

    def distance(self, df):
        corrds = df[['x','y','z']].to_numpy()
        corrds = corrds - self.p0
        distances = np.dot(self.n,corrds.T)
        return distances

    def project_coord(self,df,distance):
        corrds = df[['x','y','z']].to_numpy()
        corrds = corrds + (np.tile(self.n,(len(distance),1)) *( (-1*distance)[:,None]))
        df['x'] = corrds[:,0]
        df['y'] = corrds[:,1]
        df['z'] = corrds[:,2]
        return df
