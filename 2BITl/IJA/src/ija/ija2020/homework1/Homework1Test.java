/*
 * Zdrojové kódy jsou součástí zadání 1. úkolu pro předmětu IJA v ak. roce 2020/2021.
 * (C) Radek Kočí
 * 
 * Vytvořte třídy StoreGoods, StoreGoodsItem a StoreShelf, které splňují podmínky definované touto testovací
 * třídou. Třídy implementují příslušná rozhraní z balíku ija.ija2020.homework1.goods, která jsou součástí
 * dodaného jar archivu. 
 * Kromě metod, předepsaných rozhraními, mohou třídy implementovat své další metody a konstruktory.
 */
package ija.ija2020.homework1;

import ija.ija2020.homework1.goods.Goods;
import ija.ija2020.homework1.goods.GoodsItem;
import ija.ija2020.homework1.goods.GoodsShelf;
import ija.ija2020.homework1.goods.ReferenceShelf;
import ija.ija2020.homework1.store.StoreGoods;
import ija.ija2020.homework1.store.StoreGoodsItem;
import ija.ija2020.homework1.store.StoreShelf;
import java.time.LocalDate;
import org.junit.Test;
import org.junit.Assert;

/**
 * Testovací třída úkolu 1.
 * @author koci
 */
public class Homework1Test {

    /** Ověří základy implementace StoreGoods a StoreGoodsItem. */
    @Test
    public void test01() {
        // Vytvoreni instance zbozi se zadanym nazvem
        Goods goods1 = new StoreGoods("Stul");

        // Overeni stavu zbozi.
        Assert.assertTrue("Zadne zbozi typu Stul.", goods1.empty());
        Assert.assertEquals("Pocet zbozi typu Stul.", 0, goods1.size());

        // vlozime 2 kusy zbozi, var. 1
        // pri vytvoreni zadame zbozi, kam patri, a datum vlozeni
        GoodsItem itm11 = new StoreGoodsItem(goods1, LocalDate.of(2021, 1, 5));
        GoodsItem itm12 = new StoreGoodsItem(goods1, LocalDate.of(2021, 1, 6));
        // nasledne zavedeme do seznamu zbozi
        goods1.addItem(itm11);
        goods1.addItem(itm12);
        // vlozime kus zbozi, var. 2
        // pozadame primo zbozi o vytvoreni a evidenci kusu zbozi
        GoodsItem itm13 = goods1.newItem(LocalDate.now());

        Assert.assertFalse("Zbozi " + goods1 + " je prazdne.", goods1.empty());
        Assert.assertEquals("Pocet kusu v seznamu zbozi " + goods1, 3, goods1.size());
                     
        Assert.assertTrue("Kus zbozi odebran.", goods1.remove(itm13));
        Assert.assertEquals("Pocet kusu v seznamu zbozi " + goods1, 2, goods1.size());        
    }
    
    /** Ověří implementaci StoreShelf. */
    @Test
    public void test02() {
        GoodsShelf shelf = new StoreShelf();
        testShelf(shelf);
    }

    /** Ověří na referenční implementaci ReferenceShelf. 
     *  Tato třída je součástí dodaného jar archivu, tudíž ji neimplementujte, pouze importujte.
     */
    @Test
    public void test03() {
        GoodsShelf shelf = new ReferenceShelf();
        testShelf(shelf);
    }

    /** Ověří implementaci shelf. */
    private void testShelf(GoodsShelf shelf) {
        Goods goods1 = new StoreGoods("Stul");
        Goods goods2 = new StoreGoods("Zidle");

        GoodsItem itm11 = goods1.newItem(LocalDate.of(2021, 1, 5));
        GoodsItem itm12 = goods1.newItem(LocalDate.of(2021, 1, 6));
        GoodsItem itm13 = goods1.newItem(LocalDate.now());

        GoodsItem itm21 = goods2.newItem(LocalDate.of(2021, 2, 5));

        Assert.assertEquals("Pocet kusu v seznamu zbozi " + goods1, 3, goods1.size());
        Assert.assertEquals("Pocet kusu v seznamu zbozi " + goods2, 1, goods2.size());
        
        shelf.put(itm11);
        shelf.put(itm12);
        shelf.put(itm13);
        shelf.put(itm21);

        Assert.assertEquals("Pocet kusu zbozi " + goods1 + " v regalu", 3, shelf.size(goods1));
        Assert.assertEquals("Pocet kusu zbozi " + goods1 + " v regalu", 1, shelf.size(goods2));
        
        Goods goodsTest;
        GoodsItem itm;

        // overi, zda se vyrovna i s neexistujicim zbozim
        goodsTest = new StoreGoods("Stokrle");        
        Assert.assertFalse("Regal neobsahuje zbozi " + goodsTest, shelf.containsGoods(goodsTest));
        itm = shelf.removeAny(goodsTest);
        Assert.assertNull("Odstraneni kusu zbozi z regalu", itm);
        Assert.assertEquals("Pocet zbyvajicich kusu v regalu", 0, shelf.size(goodsTest));

        // overi, ze najde zbozi podle nazvu a id
        goodsTest = new StoreGoods("Stul");        
        Assert.assertTrue("Regal obsahuje zbozi " + goods1, shelf.containsGoods(goods1));
        Assert.assertTrue("Regal obsahuje zbozi " + goodsTest, shelf.containsGoods(goodsTest));
                
        // odstraneni zbozi z regalu
        itm = shelf.removeAny(goodsTest);
        Assert.assertNotNull("Odstraneni kusu zbozi z regalu", itm);
        Assert.assertEquals("Pocet zbyvajicich kusu v regalu", 2, shelf.size(goodsTest));
        // odstraneni zbozi ze seznamu (zbozi je prodano, vyskladneno)
        Assert.assertTrue("Odstraneni kusu zbozi z prehledu zbozi (prodano)", itm.sell());
        Assert.assertEquals("Pocet zbyvajicich kusu v seznamu zbozi pro " + goods1, 2, goods1.size());        

        // odstraneni zbozi z regalu + prodej
        itm = shelf.removeAny(goods2);
        Assert.assertNotNull("Odstraneni kusu zbozi z regalu", itm);
        Assert.assertEquals("Pocet zbyvajicich kusu v regalu", 0, shelf.size(goods2));
        Assert.assertTrue("Odstraneni kusu zbozi z prehledu zbozi (prodano)", itm.sell());
        Assert.assertEquals("Pocet zbyvajicich kusu v seznamu zbozi pro " + goods2, 0, goods2.size());        
    }
        
}
