import csv
from collections import defaultdict
from optparse import OptionParser
import itertools
import pandas as pd
from collections import defaultdict

class Apriori(object):
    #Apriori sınıfının yapıcı fonksiyonu.
    def __init__(self, minSupp, minGuven):
        if not isinstance(minSupp, (int, float)):
            raise ValueError("`minSupp` integer or float yada float olmalı")
        if not isinstance(minGuven, (int, float)):
            raise ValueError("`minGuven` integer or float yada float olmalı")
        if not 0 <= minSupp <= 1:
            raise ValueError("`minSupp`  0 ve 1 aralığında olmalıdır")
        if not 0 <= minGuven <= 1:
            raise ValueError("`minGuven` 0 ve 1 aralığında olmalıdır")
        self.minSupp = minSupp
        self.minGuven = minGuven

    #Veri setini okuyarak transaksiyon listesini döndüren yardımcı fonksiyon.
    def getTransListeKumesi(self, dosyaYolu):
        with open(dosyaYolu, 'r') as dosya:
                return [set(satir) for satir in csv.reader(dosya, delimiter=',')]
            
    #Transaksiyon listesinden tekil öge kümesini döndüren yardımcı fonksiyon.
    def getTekilOgeKumesi(self, transListeKumesi):
        return {frozenset([oge]) for satır in transListeKumesi for oge in satır}

    #Bir ögenin destek değerini hesaplayan yardımcı fonksiyon.
    def getDestek(self, oge):
        return self.ogeSayacSozlugu[oge] / self.transListeUzunlugu

    #Belirli bir terim kümesinden bir sonraki aday öge kümesini birleştirerek alıp döndüren yardımcı fonksiyon.
    def birlesikOgeSetiniAl(self, termKumesi, k):
        return set([term1.union(term2) for term1 in termKumesi for term2 in termKumesi if len(term1.union(term2)) == k])
    
    #Minimum destek değeri ile belirli bir öge kümesindeki ögeleri alıp döndüren yardımcı fonksiyon.
    def getMinSuppIleOgeleriAl(self, transactionListSet, itemSet, frequencySet, minSupp):
        updatedItemSet = set()
        localSet = dict()
        numTransactions = len(transactionListSet)

        for item in itemSet:
            itemFrequency = sum(1 for transaction in transactionListSet if item.issubset(transaction))
            frequencySet[item] += itemFrequency
            localSet[item] = itemFrequency

            support = itemFrequency / numTransactions
            if support >= minSupp:
                updatedItemSet.add(item)

        return updatedItemSet
    
    #Güven değerlerini hesaplayarak güvenSozlugu döndüren yardımcı fonksiyon.
    #(Güven)Confidence değeri örneğin 'Tavuk' alındığında 'Süt' alınma olasılığını ifade eder.
    def getConfidence(self, siklikKumesi, ogeKumesi):
        confidenceD = {}
        # her bir anahtar ve değer çifti için...
        for anahtar, deger in siklikKumesi.items():
            # her bir öge için...
            for oge in deger:
                # destek değerini hesapla
                destek = self.getDestek(oge)
                # anahtarın 1'den anahtara kadar olan değerleri üzerinde döngü oluştur
                for i in range(1, anahtar):
                    # her bir alt küme için...
                    for altKume in itertools.combinations(oge, i):
                        # alt kümeyi dondurulmuş kümeye çevir
                        altKüme = frozenset(altKume)
                        # güven değerini hesapla
                        güven = destek / self.getDestek(altKüme)
                        # güven değerini sözlüğe ekle
                        confidenceD[oge] = güven
        return confidenceD

    #Lift değerlerini hesaplayarak lift sözlüğünü döndüren yardımcı fonksiyon.
    #Lift örneğin 'Tavuk' alındığında 'süt' alınma olasılığının, 'süt'ün genel alınma olasılığına oranını ifade eder.
    def getLift(self, siklikKumesi, confidenceD):
        liftSozlugu = {}
        for oge in confidenceD:
            liftSozlugu[oge] = confidenceD[oge] / self.getDestek(oge)
        return liftSozlugu
    
    def uygula(self, dosyaYolu):
        # Transaksiyon listesini dosyadan okuyarak elde ediyoruz
        transListeKumesi = self.getTransListeKumesi(dosyaYolu)
        # Tekil öge kümesini oluşturuyoruz
        tekilOgeKumesi = self.getTekilOgeKumesi(transListeKumesi)
        # Öğe sayacı sözlüğünü oluşturmak için varsayılan bir değer atanmış sözlük oluşturuyoruz
        ogeSayacSozlugu = defaultdict(int)
        # Sıklık kümesi sözlüğünü oluşturmak için boş bir sözlük oluşturuyoruz
        siklikKumesi = dict()
        # Transaksiyon listesinin uzunluğunu kaydediyoruz
        self.transListeUzunlugu = len(transListeKumesi)
        # Tekil öge kümesini sınıfın özelliklerine atıyoruz
        self.ogeyiKumesi = tekilOgeKumesi
        # Minimum destek değeri ile tekil ögeleri alıyoruz
        tekilOgeSeti = self.getMinSuppIleOgeleriAl(transListeKumesi, tekilOgeKumesi, ogeSayacSozlugu, self.minSupp)
        # Döngü değişkeni
        k = 1
        # Şu anki sıklık seti
        simdikiSiklikSeti = tekilOgeSeti
        # ilk önce `siklikKumesi`'ni ve `k`'yı başlatıyoruz
        siklikKumesi = {}

        for _ in itertools.count():  # sonsuz bir döngü oluşturuyoruz
            # döngünün her turunda `simdikiSiklikSeti`'nin boş olup olmadığını kontrol ediyoruz
            if not simdikiSiklikSeti:  # Eğer `simdikiSiklikSeti` boşsa, döngüyü kırıyoruz
                break
            siklikKumesi[k] = simdikiSiklikSeti
            k += 1
            # Yeni aday öge setini hesaplıyoruz
            simdikiAdayOgeSeti = self.birlesikOgeSetiniAl(simdikiSiklikSeti, k)
            # Yeni sıklık setini hesaplıyoruz
            simdikiSiklikSeti = self.getMinSuppIleOgeleriAl(transListeKumesi, simdikiAdayOgeSeti, ogeSayacSozlugu, self.minSupp)
        self.ogeSayacSozlugu = ogeSayacSozlugu
        self.siklikKumesi = siklikKumesi
        # Öğe sayacı sözlüğünü ve sıklık kümesini dönüyoruz
        return ogeSayacSozlugu, siklikKumesi


if __name__ == '__main__':
    optParser = OptionParser()
    optParser.add_option('-f', '--file',dest='dosyaYolu',default="marketfisleri.txt")
    optParser.add_option('-s', '--minSupp',dest='minSupp',type='float',default=0.3)
    optParser.add_option('-c', '--minConf', dest='minConf',type='float',default=0.4)
    (options, args) = optParser.parse_args()
    dosyaYolu = options.dosyaYolu
    minSupp = options.minSupp
    minConf = options.minConf
    #print(""" \n veri: {} \n\n minimum destek: {} \n minimum güven: {} \n""".format(dosyaYolu, minSupp, minConf))
    objApriori = Apriori(minSupp, minConf)
    ogeSayacSozlugu, siklikKumesi = objApriori.uygula(dosyaYolu)
    confidenceD = objApriori.getConfidence(siklikKumesi, objApriori.ogeyiKumesi)
    liftSozlugu = objApriori.getLift(siklikKumesi, confidenceD)
    veri = []
    for anahtar, deger in siklikKumesi.items():
        for oge in deger:
            destek = objApriori.getDestek(oge)
            güven = confidenceD.get(oge, '')
            lift = liftSozlugu.get(oge, '')
            veri.append([anahtar, list(oge), destek, güven, lift])
    df = pd.DataFrame(veri, columns=["kume_id", "Ürünler", "Support(Destek)", " Confidence(Güven)", "Lift"])
    pd.set_option('display.max_colwidth', None)
    gruplanmis = df.groupby('kume_id')
    dfs = []
    for ad, grup in gruplanmis:
        print("\n{} ürünlü kümeler:".format(ad))
        grup = grup.drop(columns=['kume_id'])
        print(grup)
        dfs.append(grup)
    son_df = pd.concat(dfs, keys=['S{}'.format(n) for n in df['kume_id'].unique()])
