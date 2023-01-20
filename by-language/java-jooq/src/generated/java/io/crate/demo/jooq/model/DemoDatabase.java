/*
 * This file is generated by jOOQ.
 */
package io.crate.demo.jooq.model;


import io.crate.demo.jooq.model.tables.Author;

import java.util.Arrays;
import java.util.List;

import javax.annotation.processing.Generated;

import org.jooq.Catalog;
import org.jooq.Table;
import org.jooq.impl.SchemaImpl;


/**
 * This class is generated by jOOQ.
 */
@Generated(
        value = {
                "https://www.jooq.org",
                "jOOQ version:3.17.7"
        },
        comments = "This class is generated by jOOQ."
)
@SuppressWarnings({ "all", "unchecked", "rawtypes" })
public class DemoDatabase extends SchemaImpl {

    private static final long serialVersionUID = 1L;

    /**
     * The reference instance of <code>testdrive</code>
     */
    public static final DemoDatabase DEMO_DATABASE = new DemoDatabase();

    /**
     * The table <code>testdrive.author</code>.
     */
    public final Author AUTHOR = Author.AUTHOR;

    /**
     * No further instances allowed
     */
    private DemoDatabase() {
        super("testdrive", null);
    }


    @Override
    public Catalog getCatalog() {
        return DefaultCatalog.DEFAULT_CATALOG;
    }

    @Override
    public final List<Table<?>> getTables() {
        return Arrays.asList(
            Author.AUTHOR
        );
    }
}
