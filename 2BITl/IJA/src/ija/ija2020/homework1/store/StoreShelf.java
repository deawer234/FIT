package ija.ija2020.homework1.store;

import ija.ija2020.homework1.goods.Goods;
import ija.ija2020.homework1.goods.GoodsItem;
import ija.ija2020.homework1.goods.GoodsShelf;

public class StoreShelf implements GoodsShelf {

    @Override
    public void put(GoodsItem goodsItem) {
        
    }

    @Override
    public boolean containsGoods(Goods goods) {
        return false;
    }

    @Override
    public GoodsItem removeAny(Goods goods) {
        return null;
    }

    @Override
    public int size(Goods goods) {
        return 0;
    }
}
