CREATE INDEX idxqnaire ON qnaire USING zombodb ((qnaire.*)) WITH (url='elasticsearch:9200/', alias='qnaire');
CREATE INDEX idxevent ON event USING zombodb ((event.*)) WITH (url='elasticsearch:9200/', alias='event');
